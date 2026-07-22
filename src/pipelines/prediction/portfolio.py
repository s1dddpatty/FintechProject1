import io
import json
import joblib
import pandas as pd
import uuid
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException

from src.core.logging import get_logger

logger = get_logger(__name__)

class PortfolioScoringService:
    """Service to score an uploaded portfolio and generate analytics dynamically."""

    REQUIRED_COLUMNS = [
        "loan_amnt", "int_rate", "annual_inc", "fico_range_low", 
        "fico_range_high", "term", "grade", "home_ownership", "addr_state"
    ]
    
    COMMON_MAPPINGS = {
        "loan_amount": "loan_amnt",
        "funded_amnt": "loan_amnt",
        "interest_rate": "int_rate",
        "annual_income": "annual_inc",
        "income": "annual_inc",
        "fico_low": "fico_range_low",
        "fico_high": "fico_range_high",
        "loan_term": "term",
        "home_status": "home_ownership",
        "state": "addr_state"
    }
    
    THRESHOLDS = {
        "low": 0.20,
        "high": 0.50
    }

    def __init__(self):
        self.artifacts_dir = Path("artifacts/models")
        self.pipeline_path = self.artifacts_dir / "preprocessing_pipeline.joblib"
        self.model_path = self.artifacts_dir / "best_model.joblib"
        self.temp_dir = Path("artifacts/temp_sessions")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.preprocessor = None
        self.model = None
        self.metadata = None

    def _cleanup_old_sessions(self, max_age_seconds: int = 3600):
        """Cleans up temporary session files older than max_age_seconds."""
        now = time.time()
        for session_dir in self.temp_dir.iterdir():
            if session_dir.is_dir():
                try:
                    if now - session_dir.stat().st_mtime > max_age_seconds:
                        shutil.rmtree(session_dir)
                        logger.info(f"Cleaned up expired session: {session_dir.name}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup session {session_dir.name}: {e}")

    def _load_artifacts(self):
        """Loads required joblib artifacts or throws explicit errors."""
        if not self.pipeline_path.exists():
            raise HTTPException(status_code=500, detail="Missing preprocessing_pipeline.joblib. Please run the feature engineering pipeline.")
            
        if not self.model_path.exists():
            raise HTTPException(status_code=500, detail="Missing best_model.joblib. Please train a model first.")
            
        if self.preprocessor is None:
            self.preprocessor = joblib.load(self.pipeline_path)
            
        if self.model is None:
            self.model = joblib.load(self.model_path)
            
        if self.metadata is None:
            metadata_path = self.artifacts_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}

    async def score_portfolio(self, file: UploadFile) -> Dict[str, Any]:
        """Processes an uploaded CSV, runs preprocessing, generates predictions, and computes analytics."""
        logger.info(f"PortfolioScoringService started processing for file: {file.filename}")
        self._cleanup_old_sessions()
        start_time = time.time()
        
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported.")
            
        contents = await file.read()
        try:
            df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
            
        total_rows_uploaded = len(df)
        
        # 1. Schema Detection and Column Mapping
        original_columns = list(df.columns)
        mapped_features = {}
        ignored_columns = []
        
        # Rename columns based on common mappings (case-insensitive mapping attempt)
        df_cols_lower = {col.lower(): col for col in df.columns}
        rename_map = {}
        for uploaded_col_lower, original_col_name in df_cols_lower.items():
            if uploaded_col_lower in self.COMMON_MAPPINGS:
                target_col = self.COMMON_MAPPINGS[uploaded_col_lower]
                if target_col not in df.columns:
                    rename_map[original_col_name] = target_col
                    mapped_features[original_col_name] = target_col
        
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
            
        # Check required columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        
        # Identify ignored columns
        for col in df.columns:
            if col not in self.REQUIRED_COLUMNS and col not in ["member_id", "id", "_system_id"]:
                ignored_columns.append(col)
                
        if missing_cols:
            # If missing columns, return validation report instead of attempting inference
            return {
                "status": "validation_failed",
                "dataset_intelligence": {
                    "columns_detected": original_columns,
                    "mapped_features": mapped_features,
                    "missing_required": missing_cols,
                    "ignored_columns": ignored_columns,
                    "missing_values": df.isnull().sum().to_dict()
                },
                "error_message": "Dataset validation failed. Missing required features."
            }

        if "member_id" in df.columns:
            df["_system_id"] = df["member_id"].astype(str)
        elif "id" in df.columns:
            df["_system_id"] = df["id"].astype(str)
        else:
            df["_system_id"] = [f"APP-{i+1}" for i in range(len(df))]

        self._load_artifacts()
        
        try:
            X = self.preprocessor.transform(df)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Preprocessing failed on input data: {str(e)}")
            
        try:
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)[:, 1]
            else:
                preds = self.model.predict(X)
                probs = [0.9 if p == 1 else 0.1 for p in preds]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

        threshold = float(self.metadata.get("operating_threshold", 0.50))
        version = self.metadata.get("version", "1.0")
        
        df["probability_of_default"] = probs
        df["predicted_class"] = (df["probability_of_default"] >= threshold).astype(int)
        
        def assign_risk(p):
            if p >= self.THRESHOLDS["high"]: return "High Risk"
            elif p >= threshold: return "Medium Risk"
            else: return "Low Risk"
            
        df["risk_label"] = df["probability_of_default"].apply(assign_risk)
        
        # --- Analytics Generation ---
        total_requested_funding = float(df["loan_amnt"].sum()) if "loan_amnt" in df.columns else 0.0
        average_loan_amount = float(df["loan_amnt"].mean()) if "loan_amnt" in df.columns else 0.0
        average_income = float(df["annual_inc"].mean()) if "annual_inc" in df.columns else 0.0
        average_pd = float(df["probability_of_default"].mean())
        
        risk_counts = df["risk_label"].value_counts().to_dict()
        high_risk_count = risk_counts.get("High Risk", 0)
        low_risk_count = risk_counts.get("Low Risk", 0)
        medium_risk_count = risk_counts.get("Medium Risk", 0)
        
        # Recommended approval rate (Low + Medium risk)
        recommended_approval_rate = (low_risk_count + medium_risk_count) / total_rows_uploaded if total_rows_uploaded > 0 else 0.0
        
        # Grade Distribution
        grade_dist = df["grade"].value_counts().to_dict() if "grade" in df.columns else {}
        
        # Loan Purpose Distribution
        purpose_dist = df["purpose"].value_counts().head(10).to_dict() if "purpose" in df.columns else {}
        
        # Probability Distribution (10 bins)
        prob_dist_raw = pd.cut(df["probability_of_default"], bins=10).value_counts().sort_index()
        prob_dist = {f"{interval.left:.2f}-{interval.right:.2f}": int(count) for interval, count in prob_dist_raw.items()}
        
        # Highest Risk Segments (by Grade)
        if "grade" in df.columns:
            risk_by_grade = df.groupby("grade")["probability_of_default"].mean().sort_values(ascending=False).head(5).to_dict()
        else:
            risk_by_grade = {}

        processing_time = time.time() - start_time
        session_id = str(uuid.uuid4())
        
        # Construct full response payload
        response = {
            "status": "success",
            "session_id": session_id,
            "processing_summary": {
                "uploaded_rows": total_rows_uploaded,
                "processed_rows": total_rows_uploaded,
                "failed_rows": 0,
                "processing_time_seconds": round(processing_time, 2),
                "model_version": version,
                "algorithm": self.metadata.get("algorithm", "Unknown")
            },
            "dataset_intelligence": {
                "columns_detected": original_columns,
                "mapped_features": mapped_features,
                "missing_required": [],
                "ignored_columns": ignored_columns,
                "missing_values": df.isnull().sum().to_dict()
            },
            "executive_kpis": {
                "total_applications": total_rows_uploaded,
                "total_requested_funding": total_requested_funding,
                "average_loan_amount": average_loan_amount,
                "average_income": average_income,
                "high_risk_applications": high_risk_count,
                "low_risk_applications": low_risk_count,
                "average_pd": average_pd,
                "recommended_approval_rate": recommended_approval_rate
            },
            "charts": {
                "risk_distribution": risk_counts,
                "probability_distribution": prob_dist,
                "grade_distribution": grade_dist,
                "purpose_distribution": purpose_dist
            },
            "business_insights": {
                "highest_risk_grades": risk_by_grade,
                "portfolio_composition": f"Portfolio consists of {total_rows_uploaded} applications requesting ${total_requested_funding:,.2f}.",
                "approval_recommendation": f"Recommend approving {(recommended_approval_rate*100):.1f}% of applications."
            },
            "model_metadata": self.metadata
        }
        
        # Store temporarily
        session_dir = self.temp_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        csv_path = session_dir / "scored_portfolio.csv"
        # don't save the system_id if we generated it just now
        export_df = df.drop(columns=["_system_id"]) if "_system_id" in df.columns else df
        export_df.to_csv(csv_path, index=False)
        
        json_path = session_dir / "summary.json"
        with open(json_path, "w") as f:
            json.dump(response, f)
            
        return response

    def get_scored_csv_path(self, session_id: str) -> Path:
        """Returns the path to the scored CSV for a given session."""
        csv_path = self.temp_dir / session_id / "scored_portfolio.csv"
        if not csv_path.exists():
            raise HTTPException(status_code=404, detail="Session not found or expired.")
        return csv_path
