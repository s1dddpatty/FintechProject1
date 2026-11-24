import os
import io
import json
import joblib
import pandas as pd
import uuid
import time
import shutil
import asyncio
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
        "loan_amt": "loan_amnt",
        "principal": "loan_amnt",
        "funded_amnt": "loan_amnt",
        "amount": "loan_amnt",
        "interest_rate": "int_rate",
        "apr": "int_rate",
        "annual_income": "annual_inc",
        "income": "annual_inc",
        "salary": "annual_inc",
        "gross_income": "annual_inc",
        "income_annum": "annual_inc",
        "annum_income": "annual_inc",
        "fico_low": "fico_range_low",
        "fico_high": "fico_range_high",
        "cibil_score": "fico_score",
        "cibil": "fico_score",
        "credit_score": "fico_score",
        "bureau_score": "fico_score",
        "risk_score": "fico_score",
        "loan_term": "term",
        "duration": "term",
        "home_status": "home_ownership",
        "state": "addr_state",
        "address_state": "addr_state",
        "employment_length": "emp_length",
        "work_experience": "emp_length",
        "loan_purpose": "purpose"
    }
    
    THRESHOLDS = {
        "low": 0.15,
        "high": 0.25
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

    async def score_portfolio(self, file: Any, filename: str = None) -> Dict[str, Any]:
        """Async entry point for FastAPI compatibility."""
        if hasattr(file, "read") and asyncio.iscoroutinefunction(file.read):
            file_data = await file.read()
            fname = filename or getattr(file, "filename", "portfolio.csv")
            return self.score_portfolio_sync(file_data, filename=fname)
        return self.score_portfolio_sync(file, filename=filename)

    def score_portfolio_sync(self, file: Any, filename: str = None) -> Dict[str, Any]:
        """Synchronously processes an uploaded CSV, runs preprocessing, generates predictions, and computes analytics."""
        if filename is None:
            filename = getattr(file, "filename", os.path.basename(str(file)) if isinstance(file, (str, Path)) else "portfolio.csv")
        logger.info(f"PortfolioScoringService started processing for file: {filename}")
        self._cleanup_old_sessions()
        start_time = time.time()
        
        if not str(filename).endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported.")
            
        if isinstance(file, (bytes, bytearray)):
            try:
                df = pd.read_csv(io.BytesIO(file))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
        elif hasattr(file, "read"):
            contents = file.read()
            try:
                df = pd.read_csv(io.BytesIO(contents) if isinstance(contents, bytes) else io.StringIO(contents))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
        elif isinstance(file, (str, Path)):
            try:
                df = pd.read_csv(file)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Invalid file object provided.")
            
        total_rows_uploaded = len(df)
        
        # 1. Schema Detection and Column Mapping
        # Strip all whitespace from column headers
        df.columns = [str(c).strip() for c in df.columns]
        original_columns = list(df.columns)
        mapped_features = {}
        ignored_columns = []
        auto_imputed_features = []
        
        # Rename columns based on common mappings (case-insensitive mapping attempt)
        df_cols_lower = {col.lower().replace(" ", "_").replace("-", "_"): col for col in df.columns}
        rename_map = {}
        for uploaded_col_clean, original_col_name in df_cols_lower.items():
            if uploaded_col_clean in self.COMMON_MAPPINGS:
                target_col = self.COMMON_MAPPINGS[uploaded_col_clean]
                if target_col not in df.columns:
                    rename_map[original_col_name] = target_col
                    mapped_features[original_col_name] = target_col
        
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
        df = df.loc[:, ~df.columns.duplicated()].copy()
            
        # Universal Self-Healing Cleaner: String Sanitization
        def _clean_num(val):
            if pd.isna(val): return val
            if isinstance(val, (int, float)): return float(val)
            s = str(val).strip().replace('$', '').replace('₹', '').replace(',', '').replace('%', '').strip()
            try:
                return float(s)
            except (ValueError, TypeError):
                return None

        for num_col in ["loan_amnt", "int_rate", "annual_inc", "fico_score", "fico_range_low", "fico_range_high", "dti", "revol_util"]:
            if num_col in df.columns:
                df[num_col] = df[num_col].apply(_clean_num)

        # Single Bureau Score Mapping (e.g. CIBIL, single scalar FICO)
        if "fico_score" in df.columns:
            if "fico_range_low" not in df.columns or df["fico_range_low"].dropna().empty:
                df["fico_range_low"] = df["fico_score"] - 2.0
            if "fico_range_high" not in df.columns or df["fico_range_high"].dropna().empty:
                df["fico_range_high"] = df["fico_score"] + 2.0

        # Currency Parity Normalization (e.g. INR Lakhs/Crores vs USD)
        if "annual_inc" in df.columns and not df["annual_inc"].dropna().empty:
            inc_med = df["annual_inc"].dropna().median()
            if inc_med > 500000.0:
                scale_factor = 83.0 # Institutional USD/INR parity
                df["annual_inc"] = (df["annual_inc"] / scale_factor).round(2)
                if "loan_amnt" in df.columns:
                    df["loan_amnt"] = (df["loan_amnt"] / scale_factor).round(2)

        # Dynamic Credit Grade & Risk-Based APR Synthesis (if dataset only provides bureau score)
        if "fico_score" in df.columns and not df["fico_score"].dropna().empty:
            if "grade" not in df.columns or df["grade"].dropna().empty:
                def _derive_grade(s):
                    if pd.isna(s): return 'C'
                    if s >= 750: return 'A'
                    if s >= 700: return 'B'
                    if s >= 660: return 'C'
                    if s >= 620: return 'D'
                    if s >= 580: return 'E'
                    return 'F'
                df["grade"] = df["fico_score"].apply(_derive_grade)

            if "int_rate" not in df.columns or df["int_rate"].dropna().empty:
                grade_apr_map = {'A': 7.5, 'B': 10.5, 'C': 13.5, 'D': 16.5, 'E': 20.0, 'F': 24.0, 'G': 28.0}
                df["int_rate"] = df["grade"].map(grade_apr_map).fillna(13.0)

        if "emp_length" in df.columns:
            def _clean_emp(val):
                if pd.isna(val): return 5.0
                if isinstance(val, (int, float)): return float(val)
                s = str(val).strip()
                import re
                m = re.search(r'(\d+)', s)
                return float(m.group(1)) if m else 5.0
            df["emp_length"] = df["emp_length"].apply(_clean_emp)

        # Standardize term strings
        if "term" in df.columns:
            def _clean_term(val):
                if pd.isna(val): return " 36 months"
                s = str(val).strip()
                if "60" in s: return " 60 months"
                return " 36 months"
            df["term"] = df["term"].apply(_clean_term)

        # Self-Healing Schema Fallbacks: Ensure all Canonical Features exist
        DEFAULT_FALLBACKS = {
            "loan_amnt": 10000.0,
            "int_rate": 12.5,
            "annual_inc": 60000.0,
            "emp_length": 5.0,
            "fico_range_low": 700.0,
            "fico_range_high": 704.0,
            "term": " 36 months",
            "grade": "C",
            "home_ownership": "RENT",
            "addr_state": "CA",
            "dti": 15.0,
            "revol_util": 40.0,
            "purpose": "debt_consolidation"
        }

        for req_col, default_val in DEFAULT_FALLBACKS.items():
            if req_col not in df.columns:
                df[req_col] = default_val
                auto_imputed_features.append(req_col)
            else:
                df[req_col] = df[req_col].fillna(default_val)

        # Synthesize Advanced Financial Features if not present
        if "fico_score" not in df.columns:
            df["fico_score"] = ((df["fico_range_low"] + df["fico_range_high"]) / 2.0).round(1)

        if "installment" not in df.columns:
            # Amortization estimate
            r = (df["int_rate"] / 100.0) / 12.0
            r_safe = r.replace(0, 0.0001)
            t_num = df["term"].astype(str).str.extract(r'(\d+)')[0].astype(float).fillna(36.0)
            factor = (1.0 + r_safe) ** t_num
            df["installment"] = ((df["loan_amnt"] * (r_safe * factor)) / (factor - 1.0)).round(2).fillna((df["loan_amnt"] / 36.0).round(2))

        if "installment_to_income" not in df.columns:
            df["installment_to_income"] = ((df["installment"] * 12.0) / df["annual_inc"].replace(0, 1000.0)).round(4)

        if "loan_to_income" not in df.columns:
            df["loan_to_income"] = (df["loan_amnt"] / df["annual_inc"].replace(0, 1000.0)).round(4)

        if "grade_ordinal" not in df.columns:
            grade_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
            df["grade_ordinal"] = df["grade"].map(grade_map).fillna(3).astype(int)

        if "credit_history_months" not in df.columns:
            df["credit_history_months"] = 120.0
        
        # Identify ignored columns
        for col in original_columns:
            if col not in self.REQUIRED_COLUMNS and col not in ["member_id", "id", "_system_id"]:
                ignored_columns.append(col)

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
            elif p >= self.THRESHOLDS["low"]: return "Medium Risk"
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
        
        # Recommended approval rate (Low risk straight-through)
        recommended_approval_rate = low_risk_count / total_rows_uploaded if total_rows_uploaded > 0 else 0.0
        
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
        
        # Format scored records for tabular inspection (fast dictionary iteration)
        scored_records = []
        records_raw = df.to_dict(orient="records")
        for idx, row in enumerate(records_raw):
            f_low = row.get("fico_range_low")
            f_high = row.get("fico_range_high")
            fico_str = f"{int(float(f_low))}-{int(float(f_high))}" if pd.notna(f_low) and pd.notna(f_high) else "N/A"
            pd_val = round(float(row["probability_of_default"]), 4)
            loan_val = float(row.get("loan_amnt", 0.0) or 0.0)
            el_val = round(loan_val * pd_val * 0.45, 2)
            
            scored_records.append({
                "id": str(row.get("_system_id", f"APP-{idx+1}")),
                "loan_amnt": loan_val,
                "int_rate": float(row.get("int_rate", 0.0) or 0.0),
                "annual_inc": float(row.get("annual_inc", 0.0) or 0.0),
                "term": str(row.get("term", "36 months")).strip(),
                "grade": str(row.get("grade", "C")),
                "home_ownership": str(row.get("home_ownership", "RENT")),
                "addr_state": str(row.get("addr_state", "CA")),
                "fico": fico_str,
                "fico_range_low": float(f_low) if pd.notna(f_low) else 670.0,
                "fico_range_high": float(f_high) if pd.notna(f_high) else 674.0,
                "probability_of_default": pd_val,
                "predicted_class": int(row["predicted_class"]),
                "risk_label": str(row["risk_label"]),
                "expected_loss": el_val
            })

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
                "auto_imputed_features": auto_imputed_features,
                "ignored_columns": ignored_columns,
                "missing_values": df.isnull().sum().to_dict()
            },
            "scored_records": scored_records,
            "executive_kpis": {
                "total_applications": total_rows_uploaded,
                "total_requested_funding": total_requested_funding,
                "average_loan_amount": average_loan_amount,
                "average_income": average_income,
                "high_risk_applications": high_risk_count,
                "medium_risk_applications": medium_risk_count,
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

    def get_tableau_csv_path(self, session_id: str) -> Path:
        """Generates and returns the path to a Tableau/PowerBI optimized CSV."""
        session_dir = self.temp_dir / session_id
        tableau_csv_path = session_dir / "tableau_export.csv"
        scored_csv_path = session_dir / "scored_portfolio.csv"
        
        if not scored_csv_path.exists():
            raise HTTPException(status_code=404, detail="Session not found or expired.")
            
        if not tableau_csv_path.exists():
            df = pd.read_csv(scored_csv_path)
            # Add Tableau calculated dimensions and formatted measures
            tableau_df = pd.DataFrame({
                "Applicant_ID": df.get("id", df.get("_system_id", [f"APP-{i+1}" for i in range(len(df))])),
                "Loan_Amount_USD": df.get("loan_amnt", 0.0),
                "Interest_Rate_Pct": df.get("int_rate", 0.0),
                "Annual_Income_USD": df.get("annual_inc", 0.0),
                "Term_Duration": df.get("term", "36 months"),
                "Credit_Grade": df.get("grade", "C"),
                "State_Code": df.get("addr_state", "US"),
                "FICO_Range": df.get("fico_range_low", 670).astype(str) + "-" + df.get("fico_range_high", 674).astype(str),
                "Probability_Of_Default_PD": (df["probability_of_default"] * 100).round(2),
                "Risk_Category": df["risk_label"],
                "Credit_Policy_Decision": df["risk_label"].apply(lambda x: "APPROVED" if x == "Low Risk" else ("CONDITIONAL REVIEW" if x == "Medium Risk" else "DECLINED")),
                "Loss_Given_Default_LGD": 0.45,
                "Expected_Loss_USD": (df["loan_amnt"] * df["probability_of_default"] * 0.45).round(2)
            })
            tableau_df.to_csv(tableau_csv_path, index=False)
            
        return tableau_csv_path
