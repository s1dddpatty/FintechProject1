import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score, average_precision_score

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    XGB_AVAILABLE = False

from src.core.logging import get_logger
from .registry import ModelRegistry
from src.pipelines.feature_engineering.pipeline import build_preprocessing_pipeline
from src.pipelines.feature_engineering.data_loader import FeatureDataLoader

logger = get_logger(__name__)

class ModelTrainer:
    """
    Production-grade Quantitative Credit Risk Model Trainer.
    Trains, validates, calibrates, and benchmarks XGBoost and Random Forest classifiers
    on the 21-column canonical dataset with strict anti-leakage cross-validation.
    """
    
    def __init__(self, db_session=None):
        self.project_root = Path(__file__).resolve().parents[3]
        self.db_session = db_session
        self.artifacts_dir = self.project_root / "artifacts" / "models"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline_path = self.artifacts_dir / "preprocessing_pipeline.joblib"
        self.registry = ModelRegistry()

    def load_training_data(self, dataset_path: str = None) -> pd.DataFrame:
        """Loads canonical 150k dataset or falls back to database records."""
        candidate_paths = [
            dataset_path,
            self.project_root / "data" / "cleaned_model_ready_150k.csv",
            self.project_root / "artifacts" / "pipeline_sessions" / "cc42f61b-e88" / "cleaned_model_ready.csv",
            self.project_root / "data" / "cleaned_model_ready.csv"
        ]
        
        for p in candidate_paths:
            if p:
                path_obj = Path(p)
                if path_obj.exists():
                    logger.info(f"Loading high-volume canonical credit dataset from: {path_obj}")
                    df = pd.read_csv(path_obj)
                    logger.info(f"Successfully loaded {len(df):,} records with {len(df.columns)} canonical columns.")
                    return df

        if self.db_session:
            logger.info("No canonical CSV found; loading from database session...")
            loader = FeatureDataLoader(self.db_session)
            df = loader.load_raw_features()
            if not df.empty:
                return df

        raise FileNotFoundError(f"No training dataset found in {self.project_root / 'data'}")

    def train(self, dataset_path: str = None) -> Dict[str, Any]:
        """Executes the complete, leakage-free ML training and evaluation pipeline."""
        start_time = time.time()
        logger.info("Initializing Enterprise Credit Risk Model Training Engine...")

        # 1. Load Data
        df = self.load_training_data(dataset_path)
        
        # 2. Extract Ground Truth Binary Target (y)
        if "loan_status" not in df.columns:
            raise ValueError("Target column 'loan_status' missing from training dataset.")
            
        # Target mapping: 1 for Default / Charged Off, 0 for Fully Paid
        df["is_default"] = df["loan_status"].astype(str).str.strip().isin(["Charged Off", "Default"]).astype(int)
        y = df["is_default"]
        X_raw = df.drop(columns=["is_default", "loan_status", "id"], errors="ignore")
        
        total_rows = len(df)
        default_count = int(y.sum())
        fully_paid_count = total_rows - default_count
        imbalance_ratio = round(fully_paid_count / max(1, default_count), 2)
        
        logger.info(f"Cohort Size: {total_rows:,} records | Defaults: {default_count:,} ({y.mean()*100:.1f}%) | Non-Defaults: {fully_paid_count:,} | Imbalance: {imbalance_ratio}:1")

        # 3. Stratified Partitioning (70% Train, 15% Validation, 15% Holdout Test)
        logger.info("Partitioning dataset into Stratified Train (70%), Val (15%), and Test (15%) splits...")
        X_train_raw, X_temp_raw, y_train, y_temp = train_test_split(
            X_raw, y, test_size=0.30, stratify=y, random_state=42
        )
        X_val_raw, X_test_raw, y_val, y_test = train_test_split(
            X_temp_raw, y_temp, test_size=0.50, stratify=y_temp, random_state=42
        )
        
        logger.info(f"Split sizes -> Train: {len(X_train_raw):,} | Val: {len(X_val_raw):,} | Test: {len(X_test_raw):,}")

        # 4. Strict Leak-Free Pipeline Preprocessing (Fit on Train ONLY)
        logger.info("Fitting Mathematical Preprocessing Pipeline strictly on Training set...")
        preprocessor = build_preprocessing_pipeline()
        preprocessor.fit(X_train_raw)
        
        # Transform splits
        X_train = preprocessor.transform(X_train_raw)
        X_val = preprocessor.transform(X_val_raw)
        X_test = preprocessor.transform(X_test_raw)
        
        feature_count = X_train.shape[1]
        logger.info(f"Transformed feature tensor dimensions: {feature_count} numerical attributes.")
        
        # Save fitted preprocessing pipeline
        joblib.dump(preprocessor, self.pipeline_path)
        logger.info(f"Fitted preprocessing pipeline persisted to {self.pipeline_path}")

        # 5. Stratified 5-Fold Cross-Validation on Training Set
        logger.info("Executing 5-Fold Stratified Cross-Validation on training folds...")
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_auc_scores = []
        for fold, (train_idx, fold_val_idx) in enumerate(skf.split(X_train, y_train)):
            X_cv_tr, y_cv_tr = X_train[train_idx], y_train.iloc[train_idx]
            X_cv_va, y_cv_va = X_train[fold_val_idx], y_train.iloc[fold_val_idx]
            
            fold_rf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
            fold_rf.fit(X_cv_tr, y_cv_tr)
            fold_score = roc_auc_score(y_cv_va, fold_rf.predict_proba(X_cv_va)[:, 1])
            cv_auc_scores.append(round(float(fold_score), 4))
            
        cv_mean = float(np.mean(cv_auc_scores))
        cv_std = float(np.std(cv_auc_scores))
        logger.info(f"5-Fold CV Mean ROC-AUC: {cv_mean:.4f} (+/- {cv_std:.4f}) -> {cv_auc_scores}")

        # 6. Model Training & Validation
        evaluations = []

        # Model A: XGBoost Classifier (Champion Candidate)
        if XGB_AVAILABLE:
            logger.info("Training XGBoost with cost-sensitive loss weighting (scale_pos_weight=4.0)...")
            xgb = XGBClassifier(
                n_estimators=350,
                learning_rate=0.05,
                max_depth=5,
                min_child_weight=30,
                subsample=0.80,
                colsample_bytree=0.80,
                reg_alpha=0.1,
                reg_lambda=1.5,
                scale_pos_weight=imbalance_ratio,
                random_state=42,
                eval_metric="logloss",
                n_jobs=-1
            )
            xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
            evaluations.append({"name": "XGBoost", "model": xgb})

        # Model B: Random Forest Classifier (Challenger Candidate)
        logger.info("Training Random Forest with balanced subsample bagging...")
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=14,
            min_samples_split=20,
            min_samples_leaf=10,
            max_features="sqrt",
            class_weight="balanced_subsample",
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)
        evaluations.append({"name": "Random Forest", "model": rf})

        # 7. Operating Threshold Calibration (Tuned on 22,500 Validation Records)
        for ev in evaluations:
            m_name = ev["name"]
            m_obj = ev["model"]
            probs_val = m_obj.predict_proba(X_val)[:, 1]
            
            thresholds = np.arange(0.10, 0.71, 0.02)
            best_thresh = 0.50
            best_f1 = -1.0
            
            for t in thresholds:
                preds_val = (probs_val >= t).astype(int)
                f1 = f1_score(y_val, preds_val, zero_division=0)
                if f1 > best_f1:
                    best_f1 = f1
                    best_thresh = float(t)
                    
            logger.info(f"{m_name} Calibrated Optimal Threshold: {best_thresh:.2f} (Val F1: {best_f1:.4f})")
            ev["operating_threshold"] = best_thresh

            # 8. Unbiased Evaluation on 22,500 Holdout Test Records
            test_metrics = self.registry.evaluate_model(m_obj, X_test, y_test, threshold=best_thresh)
            ev["metrics"] = test_metrics
            logger.info(f"{m_name} Test Set Evaluation -> ROC-AUC: {test_metrics['roc_auc']:.4f} | PR-AUC: {test_metrics['pr_auc']:.4f} | Recall: {test_metrics['recall']:.4f} | F1: {test_metrics['f1']:.4f}")

        # 9. Champion Selection
        champion = self.registry.select_best_model(evaluations)
        challenger = next((ev for ev in evaluations if ev["name"] != champion["name"]), None)

        # 10. Metadata Compilation & Persistence
        elapsed_time = round(time.time() - start_time, 2)
        metadata_extras = {
            "operating_threshold": champion["operating_threshold"],
            "threshold_selection_metric": "F1-Score Cost-Utility",
            "algorithm": champion["name"],
            "trained_on_rows": len(y_train),
            "validation_rows": len(y_val),
            "test_rows": len(y_test),
            "total_dataset_rows": total_rows,
            "training_duration_seconds": elapsed_time,
            "training_timestamp": datetime.utcnow().isoformat(),
            "roc_auc": champion["metrics"]["roc_auc"],
            "gini_coefficient": champion["metrics"]["gini_coefficient"],
            "ks_statistic": champion["metrics"]["ks_statistic"],
            "pr_auc": champion["metrics"]["pr_auc"],
            "precision": champion["metrics"]["precision"],
            "recall": champion["metrics"]["recall"],
            "f1": champion["metrics"]["f1"],
            "brier_score": champion["metrics"]["brier_score"],
            "feature_count": feature_count,
            "cross_validation": {
                "folds": 5,
                "strategy": "StratifiedKFold",
                "mean_roc_auc": cv_mean,
                "std_roc_auc": cv_std,
                "fold_scores": cv_auc_scores
            },
            "class_distribution": {
                "non_defaults": fully_paid_count,
                "defaults": default_count,
                "imbalance_ratio": f"{imbalance_ratio}:1"
            },
            "model_comparison": [
                {
                    "name": ev["name"],
                    "is_champion": (ev["name"] == champion["name"]),
                    "roc_auc": ev["metrics"]["roc_auc"],
                    "gini_coefficient": ev["metrics"]["gini_coefficient"],
                    "ks_statistic": ev["metrics"]["ks_statistic"],
                    "pr_auc": ev["metrics"]["pr_auc"],
                    "f1": ev["metrics"]["f1"],
                    "precision": ev["metrics"]["precision"],
                    "recall": ev["metrics"]["recall"],
                    "brier_score": ev["metrics"]["brier_score"],
                    "operating_threshold": ev["operating_threshold"]
                } for ev in evaluations
            ]
        }

        saved_metadata = self.registry.persist_models(champion, challenger, metadata_extras)
        logger.info(f"Model Training Pipeline completed in {elapsed_time}s! Champion: {champion['name']} (ROC-AUC: {champion['metrics']['roc_auc']:.4f})")
        return saved_metadata
