import os
import re
import uuid
import json
import time
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from src.core.logging import get_logger
from src.services.llm import LLMService

logger = get_logger(__name__)

class UniversalCleaningPipeline:
    """
    Production Ingestion, Type Sanitization, and Advanced Financial Feature Engineering Pipeline.
    Transforms raw, unformatted, or dirty CSV datasets into institutional, model-ready datasets
    and generates an automated AI Transformation Audit Memorandum via local Ollama.
    """

    # Comprehensive dictionary mapping common real-world column aliases to canonical schema
    ALIAS_MAP = {
        # Loan Amount
        "loan_amount": "loan_amnt", "loan_amt": "loan_amnt", "requested_amount": "loan_amnt",
        "loan_size": "loan_amnt", "amount": "loan_amnt", "principal": "loan_amnt",
        
        # Funded Amount
        "funded_amount": "funded_amnt", "funded_amt": "funded_amnt", "funded": "funded_amnt",
        
        # Interest Rate
        "interest_rate": "int_rate", "rate": "int_rate", "apr": "int_rate", "interest": "int_rate",
        
        # Term Duration
        "loan_term": "term", "duration": "term", "months": "term", "period": "term",
        
        # Credit Grade
        "credit_grade": "grade", "risk_grade": "grade", "rating": "grade",
        "subgrade": "sub_grade", "sub_rating": "sub_grade",
        
        # Annual Income
        "annual_income": "annual_inc", "income": "annual_inc", "salary": "annual_inc", "gross_income": "annual_inc",
        
        # Housing / Home Ownership
        "home_status": "home_ownership", "residence_status": "home_ownership", "housing": "home_ownership",
        
        # State
        "state": "addr_state", "address_state": "addr_state", "borrower_state": "addr_state", "location": "addr_state",
        
        # FICO Scores
        "fico_low": "fico_range_low", "fico_score_low": "fico_range_low", "credit_score_low": "fico_range_low", "fico": "fico_range_low",
        "fico_high": "fico_range_high", "fico_score_high": "fico_range_high", "credit_score_high": "fico_range_high",
        
        # Installment
        "monthly_payment": "installment", "payment": "installment", "monthly_installment": "installment",
        
        # Debt to Income
        "debt_to_income": "dti", "dti_ratio": "dti", "debt_income_ratio": "dti",
        
        # Credit Utilization
        "revolving_utilization": "revol_util", "credit_utilization": "revol_util", "utilization": "revol_util",
        
        # Dates
        "credit_history_start": "earliest_cr_line", "first_credit_line": "earliest_cr_line",
        "issue_date": "issue_d", "origination_date": "issue_d", "loan_date": "issue_d",
        
        # Purpose & Employment
        "loan_purpose": "purpose", "reason": "purpose",
        "employment_length": "emp_length", "job_duration": "emp_length", "employment_years": "emp_length",
        "work_experience": "emp_length", "experience": "emp_length", "years_employed": "emp_length",
        "emp_len": "emp_length", "job_years": "emp_length", "work_years": "emp_length", "employment": "emp_length"
    }

    GRADE_ORDINAL_MAP = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7
    }

    # Strict Canonical Schema: 1 Primary Key + 3 Entities + 1 Solvency Stream (21 columns)
    CANONICAL_COLUMNS = [
        # Primary Key
        "id",
        # Domain 1: Individual / Borrower Profile (4 features)
        "annual_inc", "emp_length", "home_ownership", "addr_state",
        # Domain 2: Credit Bureau Profile (6 features)
        "fico_score", "fico_range_low", "fico_range_high", "dti", "revol_util", "credit_history_months",
        # Domain 3: Loan Facility / Contract Terms (7 features)
        "loan_amnt", "term", "int_rate", "installment", "grade", "grade_ordinal", "purpose",
        # Domain 4: Solvency & Performance Stream (3 features)
        "installment_to_income", "loan_to_income", "loan_status"
    ]

    DOMAIN_GROUPS = {
        "Borrower Profile": {
            "entity": "Individual / Borrower Profile",
            "description": "Demographic, employment stability, and gross liquidity attributes.",
            "columns": ["annual_inc", "emp_length", "home_ownership", "addr_state"]
        },
        "Credit Bureau": {
            "entity": "Credit Bureau Profile",
            "description": "External bureau risk metrics, historical debt ratios, and credit history tenure.",
            "columns": ["fico_score", "fico_range_low", "fico_range_high", "dti", "revol_util", "credit_history_months"]
        },
        "Loan Facility": {
            "entity": "Loan Facility / Agreement",
            "description": "Contractual loan underwriting terms, interest rates, and risk grade assignments.",
            "columns": ["loan_amnt", "term", "int_rate", "installment", "grade", "grade_ordinal", "purpose"]
        },
        "Solvency Stream": {
            "entity": "Solvency & Performance Stream",
            "description": "Dynamic debt burden ratios (PTI/LTI) and loan lifecycle trajectory state.",
            "columns": ["installment_to_income", "loan_to_income", "loan_status"]
        }
    }

    def __init__(self):
        self.output_dir = Path("artifacts/pipeline_sessions")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.llm_service = LLMService()

    @staticmethod
    def _clean_num(val):
        """Sanitizes currency symbols ($/₹), commas, percentages, and spaces into clean floats."""
        if pd.isna(val):
            return np.nan
        if isinstance(val, (int, float)):
            return float(val)
        cleaned = re.sub(r'[\$,₹,%, ]', '', str(val).strip())
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return np.nan

    @staticmethod
    def _clean_term(val):
        """Extracts numeric month duration from strings like '36 months', '60 mo' -> 36, 60."""
        if pd.isna(val):
            return 36
        match = re.search(r'\d+', str(val))
        return int(match.group()) if match else 36

    @staticmethod
    def _clean_emp_length(val):
        """Parses employment strings like '10+ years' -> 10, '< 1 year' -> 0, '5 years' -> 5."""
        if pd.isna(val):
            return 5.0
        val_str = str(val).strip().lower()
        if "10+" in val_str:
            return 10.0
        if "< 1" in val_str or "<1" in val_str:
            return 0.0
        match = re.search(r'\d+', val_str)
        return float(match.group()) if match else 5.0

    @staticmethod
    def _calculate_installment(principal: float, annual_rate_pct: float, term_months: int) -> float:
        """Computes standard financial monthly loan installment using amortization equation."""
        if principal <= 0 or term_months <= 0:
            return 0.0
        r = (annual_rate_pct / 100.0) / 12.0
        if r <= 0:
            return round(principal / term_months, 2)
        factor = (1.0 + r) ** term_months
        payment = principal * (r * factor) / (factor - 1.0)
        return round(float(payment), 2)

    async def process_dataset(self, file_path_or_buffer, original_filename: str = "dataset.csv") -> dict:
        """
        Executes end-to-end ingestion, schema normalization, type sanitization,
        advanced financial feature engineering, quality scoring, and LLM audit generation.
        """
        start_time = time.time()
        session_id = str(uuid.uuid4())[:12]
        session_folder = self.output_dir / session_id
        session_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting Universal Cleaning Pipeline for {original_filename} (Session: {session_id})")

        # 1. Ingestion: Load raw DataFrame
        try:
            if hasattr(file_path_or_buffer, "read"):
                df_raw = pd.read_csv(file_path_or_buffer, encoding_errors="replace")
            else:
                df_raw = pd.read_csv(file_path_or_buffer, encoding_errors="replace")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

        raw_rows_count = len(df_raw)
        raw_cols_count = len(df_raw.columns)
        logger.info(f"Loaded raw dataset with {raw_rows_count} rows and {raw_cols_count} columns.")

        # Telemetry tracking dictionaries
        mapped_aliases = {}
        sanitized_columns = {}
        imputed_features = []
        engineered_features = {}

        df = df_raw.copy()

        # 2. Autonomous Schema Normalization (LLM + Semantic Matcher)
        sample_records = df.head(3).to_dict(orient="records") if len(df) > 0 else []
        llm_mapped = await self.llm_service.resolve_schema_mapping(list(df.columns), sample_records)
        
        norm_cols = {}
        for col in df.columns:
            if col in llm_mapped:
                canonical = llm_mapped[col]
                norm_cols[col] = canonical
                mapped_aliases[col] = canonical
            else:
                clean_name = str(col).strip().lower().replace(" ", "_").replace("-", "_")
                if clean_name in self.ALIAS_MAP:
                    canonical = self.ALIAS_MAP[clean_name]
                    norm_cols[col] = canonical
                    mapped_aliases[col] = canonical
                else:
                    norm_cols[col] = clean_name
        df.rename(columns=norm_cols, inplace=True)

        # 3. Universal Type Sanitization
        num_fields_to_clean = ["loan_amnt", "funded_amnt", "int_rate", "annual_inc", "fico_range_low", "fico_range_high", "installment", "dti", "revol_util"]
        for field in num_fields_to_clean:
            if field in df.columns:
                pre_nulls = df[field].isna().sum()
                df[field] = df[field].apply(self._clean_num)
                post_nulls = df[field].isna().sum()
                sanitized_columns[field] = f"Parsed currency/percent strings to float ({post_nulls - pre_nulls} unparseable values converted to null)."

        if "term" in df.columns:
            df["term"] = df["term"].apply(self._clean_term)
            sanitized_columns["term"] = "Extracted numeric loan duration in months (e.g. 36 or 60)."

        if "emp_length" in df.columns:
            df["emp_length"] = df["emp_length"].apply(self._clean_emp_length)
            sanitized_columns["emp_length"] = "Parsed employment duration to numeric years."

        # Standardize decimal fraction rates and ratios to standard percentage points (e.g. 0.1527 -> 15.27%)
        if "int_rate" in df.columns and not df["int_rate"].dropna().empty and (df["int_rate"].dropna() <= 1.0).all():
            df["int_rate"] = (df["int_rate"] * 100.0).round(2)
            sanitized_columns["int_rate"] = "Normalized decimal fraction interest rate to percentage points (e.g. 0.1527 → 15.27%)."

        if "dti" in df.columns and not df["dti"].dropna().empty and (df["dti"].dropna() <= 1.5).all():
            df["dti"] = (df["dti"] * 100.0).round(2)
            sanitized_columns["dti"] = "Normalized decimal fraction debt-to-income ratio to percentage points (e.g. 0.2088 → 20.88%)."

        if "revol_util" in df.columns and not df["revol_util"].dropna().empty and (df["revol_util"].dropna() <= 1.5).all():
            df["revol_util"] = (df["revol_util"] * 100.0).round(2)
            sanitized_columns["revol_util"] = "Normalized decimal fraction revolving utilization to percentage points."

        # 4. Declarative Invariant Schema Specification & Universal Imputation
        CANONICAL_SPEC = {
            "annual_inc": {"default": 65000.0, "type": float, "impute": "median", "desc": "gross income $65,000"},
            "emp_length": {"default": 5.0, "type": float, "impute": "median", "desc": "employment tenure 5.0 years"},
            "home_ownership": {"default": "RENT", "type": str, "impute": "mode", "desc": "home ownership 'RENT'"},
            "addr_state": {"default": "CA", "type": str, "impute": "mode", "desc": "geographic baseline 'CA'"},
            "fico_range_low": {"default": 680.0, "type": float, "impute": "median", "desc": "FICO range low 680.0"},
            "fico_range_high": {"default": 684.0, "type": float, "impute": "offset_fico", "desc": "FICO range high 684.0"},
            "dti": {"default": 15.0, "type": float, "impute": "median", "desc": "debt-to-income 15.0%"},
            "revol_util": {"default": 40.0, "type": float, "impute": "median", "desc": "revolving utilization 40.0%"},
            "loan_amnt": {"default": 10000.0, "type": float, "impute": "median", "desc": "loan size $10,000"},
            "term": {"default": 36, "type": int, "impute": "mode", "desc": "tenor 36 months"},
            "int_rate": {"default": 13.0, "type": float, "impute": "median", "desc": "interest rate 13.0%"},
            "grade": {"default": "C", "type": str, "impute": "mode", "desc": "credit grade C"},
            "purpose": {"default": "debt_consolidation", "type": str, "impute": "mode", "desc": "purpose 'debt_consolidation'"},
            "loan_status": {"default": "UNSCORED", "type": str, "impute": "mode", "desc": "status 'UNSCORED'"}
        }

        for col_name, spec in CANONICAL_SPEC.items():
            if col_name not in df.columns or df[col_name].dropna().empty:
                df[col_name] = spec["default"]
                imputed_features.append(f"{col_name} (Injected domain prior: {spec['desc']})")
            else:
                if spec["impute"] == "median":
                    med_val = df[col_name].median() if not df[col_name].dropna().empty else spec["default"]
                    df[col_name] = df[col_name].fillna(med_val)
                elif spec["impute"] == "mode":
                    mode_val = df[col_name].mode()[0] if not df[col_name].dropna().empty else spec["default"]
                    df[col_name] = df[col_name].fillna(mode_val)
                elif spec["impute"] == "offset_fico":
                    df[col_name] = df[col_name].fillna(df["fico_range_low"] + 4.0)

        # Standardize string fields
        df["grade"] = df["grade"].astype(str).str.upper().str.strip()
        df["home_ownership"] = df["home_ownership"].astype(str).str.upper().str.strip()
        df["addr_state"] = df["addr_state"].astype(str).str.upper().str.strip()
        df["purpose"] = df["purpose"].astype(str).str.lower().str.strip()
        df["term"] = df["term"].astype(int)

        # Primary Key (ID) Invariant
        if "id" not in df.columns:
            df["id"] = [f"LNC-{1000000 + i}" for i in range(len(df))]
        else:
            df["id"] = df["id"].fillna("").astype(str)
            mask = (df["id"] == "") | (df["id"].str.lower() == "nan")
            if mask.any():
                df.loc[mask, "id"] = [f"LNC-{1000000 + i}" for i in range(mask.sum())]

        df["loan_status"] = df["loan_status"].fillna("UNSCORED").astype(str).str.strip()

        # 5. Advanced Financial Feature Engineering
        # Feature A: Credit Score Midpoint (FICO Score)
        df["fico_score"] = ((df["fico_range_low"] + df["fico_range_high"]) / 2.0).round(1)
        engineered_features["fico_score"] = "Arithmetic midpoint of FICO range bounds representing definitive credit score."

        # Feature B: Monthly Installment Calculation (Vectorized fixed-rate amortization)
        if "installment" not in df.columns or df["installment"].isna().all():
            r = (df["int_rate"] / 100.0) / 12.0
            r_safe = r.replace(0, 0.0001)
            factor = (1.0 + r_safe) ** df["term"]
            computed_inst = (df["loan_amnt"] * (r_safe * factor)) / (factor - 1.0)
            df["installment"] = computed_inst.round(2).fillna((df["loan_amnt"] / df["term"]).round(2))
            engineered_features["installment"] = "Computed monthly debt servicing obligation using fixed-rate amortization equation."
        else:
            df["installment"] = df["installment"].fillna(
                (df["loan_amnt"] * (df["int_rate"] / 100.0 / 12.0)).round(2)
            )

        # Feature C: Payment-to-Income (PTI Ratio)
        df["installment_to_income"] = (
            (df["installment"] * 12.0) / df["annual_inc"].replace(0, 1000.0)
        ).round(4)
        engineered_features["installment_to_income"] = "Annual debt payment relative to annual gross liquidity (PTI debt burden ratio)."

        # Feature D: Loan-to-Income Ratio
        df["loan_to_income"] = (
            df["loan_amnt"] / df["annual_inc"].replace(0, 1000.0)
        ).round(4)
        engineered_features["loan_to_income"] = "Principal loan exposure relative to annual earnings leverage."

        # Feature E: Monotonic Grade Ordinal
        df["grade_ordinal"] = df["grade"].map(self.GRADE_ORDINAL_MAP).fillna(3).astype(int)
        engineered_features["grade_ordinal"] = "Ordinal integer mapping (A=1 ... G=7) enabling monotonic tree split optimization."

        # Feature F: Credit History Length (Months)
        if "earliest_cr_line" in df.columns and "issue_d" in df.columns:
            try:
                earliest_dt = pd.to_datetime(df["earliest_cr_line"], errors="coerce")
                issue_dt = pd.to_datetime(df["issue_d"], errors="coerce")
                months_diff = ((issue_dt - earliest_dt).dt.days / 30.4375).round(0)
                df["credit_history_months"] = months_diff.fillna(120.0).clip(lower=12)
                engineered_features["credit_history_months"] = "Tenure of borrower credit profile in months from first credit line opening."
            except Exception:
                df["credit_history_months"] = 120.0
        else:
            df["credit_history_months"] = 120.0
            engineered_features["credit_history_months"] = "Benchmark 10-year credit profile maturity (120 months)."

        # 6. Canonical Enterprise Schema Partitioning (3 Entities + 1 Solvency Stream)
        # Defensive schema enforcement: Guarantee every canonical column exists prior to selection
        DEFAULT_CANONICAL_VALUES = {
            "id": [f"LNC-{1000000 + i}" for i in range(len(df))],
            "annual_inc": 65000.0,
            "emp_length": 5.0,
            "home_ownership": "RENT",
            "addr_state": "CA",
            "fico_score": 682.0,
            "fico_range_low": 680.0,
            "fico_range_high": 684.0,
            "dti": 15.0,
            "revol_util": 40.0,
            "credit_history_months": 120.0,
            "loan_amnt": 10000.0,
            "term": 36,
            "int_rate": 13.0,
            "installment": 336.93,
            "grade": "C",
            "grade_ordinal": 3,
            "purpose": "debt_consolidation",
            "installment_to_income": 0.0622,
            "loan_to_income": 0.1538,
            "loan_status": "UNSCORED"
        }
        for col in self.CANONICAL_COLUMNS:
            if col not in df.columns:
                df[col] = DEFAULT_CANONICAL_VALUES.get(col, 0.0)

        # Select and reorder strictly to the 21 fixed canonical columns
        df_canonical = df[self.CANONICAL_COLUMNS].copy()

        # Final pass: Guarantee 100% null elimination across canonical features
        for col in df_canonical.columns:
            if df_canonical[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                df_canonical[col] = df_canonical[col].fillna(0.0)
            else:
                df_canonical[col] = df_canonical[col].fillna("N/A")

        # 7. Quality Scoring
        missing_cells_after = df_canonical.isnull().sum().sum()
        total_cells = df_canonical.shape[0] * df_canonical.shape[1]
        completeness_ratio = 1.0 - (missing_cells_after / max(1, total_cells))
        
        # Penalties: Deduct for heavy alias remapping or raw missingness
        penalty = min(20, len(mapped_aliases) * 1.5 + len(imputed_features) * 2.0)
        data_quality_score = max(60, min(100, int(completeness_ratio * 100 - penalty)))

        # 8. Persist Clean Model-Ready Output (strictly 21 canonical columns)
        clean_csv_path = session_folder / "cleaned_model_ready.csv"
        df_canonical.to_csv(clean_csv_path, index=False)

        # 9. Compile Telemetry & Invoke LLM Audit
        telemetry = {
            "raw_rows": raw_rows_count,
            "cleaned_rows": len(df_canonical),
            "raw_columns_count": raw_cols_count,
            "cleaned_columns_count": len(df_canonical.columns),
            "canonical_columns_count": len(self.CANONICAL_COLUMNS),
            "data_quality_score": data_quality_score,
            "mapped_aliases": mapped_aliases,
            "sanitized_columns": sanitized_columns,
            "imputed_features": imputed_features,
            "engineered_features": engineered_features,
            "dropped_rows": raw_rows_count - len(df_canonical)
        }

        logger.info("Requesting Executive Data Quality & Transformation Audit Memorandum from LLM...")
        llm_response = await self.llm_service.generate_pipeline_audit(telemetry)

        # Save summary JSON
        summary_payload = {
            "session_id": session_id,
            "original_filename": original_filename,
            "processed_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "processing_time_seconds": round(time.time() - start_time, 2),
            "data_quality_score": data_quality_score,
            "telemetry": telemetry,
            "canonical_columns": self.CANONICAL_COLUMNS,
            "domain_groups": self.DOMAIN_GROUPS,
            "llm_audit": llm_response,
            "preview_records": df_canonical.head(50).fillna("N/A").to_dict(orient="records")
        }

        with open(session_folder / "summary.json", "w") as f:
            json.dump(summary_payload, f, indent=2)

        logger.info(f"Universal Cleaning Pipeline completed successfully in {summary_payload['processing_time_seconds']}s")
        return summary_payload

    def get_clean_csv_path(self, session_id: str) -> Path:
        """Retrieves absolute path to the cleaned, model-ready CSV file."""
        csv_path = self.output_dir / session_id / "cleaned_model_ready.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Cleaned dataset session {session_id} not found.")
        return csv_path
