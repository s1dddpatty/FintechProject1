import json
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, average_precision_score,
    brier_score_loss, confusion_matrix, roc_curve, precision_recall_curve
)
from scipy.stats import ks_2samp
from src.core.logging import get_logger

logger = get_logger(__name__)

class ModelRegistry:
    """Evaluates models, selects champion vs challenger, and persists production artifacts."""
    
    def __init__(self, artifacts_dir: Path = None):
        if artifacts_dir:
            self.artifacts_dir = Path(artifacts_dir)
        else:
            self.artifacts_dir = Path(__file__).resolve().parents[3] / "artifacts" / "models"
            
        self.best_model_path = self.artifacts_dir / "best_model.joblib"
        self.challenger_model_path = self.artifacts_dir / "challenger_model.joblib"
        self.metadata_path = self.artifacts_dir / "metadata.json"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_model(self, model, X_test, y_test, threshold: float = 0.5) -> Dict[str, Any]:
        """Calculates comprehensive quantitative credit risk evaluation metrics."""
        probs = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_test)[:, 1]
            preds = (probs >= threshold).astype(int)
            roc_auc = float(roc_auc_score(y_test, probs))
            pr_auc = float(average_precision_score(y_test, probs))
            brier = float(brier_score_loss(y_test, probs))
        else:
            preds = model.predict(X_test)
            roc_auc = float(roc_auc_score(y_test, preds))
            pr_auc = float(precision_score(y_test, preds, zero_division=0))
            brier = float(brier_score_loss(y_test, preds))
            
        cm = confusion_matrix(y_test, preds)
        
        # Calculate KS Statistic and Gini Coefficient
        y_test_arr = np.array(y_test)
        if probs is not None:
            default_probs = probs[y_test_arr == 1]
            non_default_probs = probs[y_test_arr == 0]
            if len(default_probs) > 0 and len(non_default_probs) > 0:
                ks_stat = float(ks_2samp(default_probs, non_default_probs).statistic)
            else:
                ks_stat = 0.0
        else:
            ks_stat = 0.0
        gini = float(2.0 * roc_auc - 1.0)
        
        # Calculate ROC and PR curves (downsampled to 40 representative points for lightweight JSON)
        roc_pts = []
        pr_pts = []
        if probs is not None:
            fpr, tpr, _ = roc_curve(y_test, probs)
            step = max(1, len(fpr) // 40)
            roc_pts = [{"fpr": round(float(f), 4), "tpr": round(float(t), 4)} for f, t in zip(fpr[::step], tpr[::step])]
            
            prec, rec, _ = precision_recall_curve(y_test, probs)
            step_pr = max(1, len(prec) // 40)
            pr_pts = [{"recall": round(float(r), 4), "precision": round(float(p), 4)} for r, p in zip(rec[::step_pr], prec[::step_pr])]

        metrics = {
            "accuracy": float(accuracy_score(y_test, preds)),
            "precision": float(precision_score(y_test, preds, zero_division=0)),
            "recall": float(recall_score(y_test, preds, zero_division=0)),
            "f1": float(f1_score(y_test, preds, zero_division=0)),
            "roc_auc": roc_auc,
            "gini_coefficient": gini,
            "ks_statistic": ks_stat,
            "pr_auc": pr_auc,
            "brier_score": brier,
            "confusion_matrix": cm.tolist(),
            "roc_curve": roc_pts,
            "pr_curve": pr_pts
        }
        return metrics

    def select_best_model(self, model_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Selects the champion model primarily based on PR-AUC & ROC-AUC."""
        best_eval = max(model_evaluations, key=lambda x: (x["metrics"]["pr_auc"] + x["metrics"]["roc_auc"]))
        logger.info(f"Selected champion model: {best_eval['name']} (ROC-AUC: {best_eval['metrics']['roc_auc']:.4f}, PR-AUC: {best_eval['metrics']['pr_auc']:.4f})")
        return best_eval

    def persist_models(self, champion_eval: Dict[str, Any], challenger_eval: Dict[str, Any], metadata_extras: Dict[str, Any]):
        """Saves champion and challenger models and writes full production metadata."""
        # Save Champion
        joblib.dump(champion_eval["model"], self.best_model_path)
        logger.info(f"Champion model saved to {self.best_model_path}")
        
        # Save Challenger
        if challenger_eval:
            joblib.dump(challenger_eval["model"], self.challenger_model_path)
            logger.info(f"Challenger model saved to {self.challenger_model_path}")
        
        metadata = {
            "model_name": champion_eval["name"],
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            **metadata_extras,
            "metrics": champion_eval["metrics"]
        }
        
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Metadata saved to {self.metadata_path}")
        return metadata
