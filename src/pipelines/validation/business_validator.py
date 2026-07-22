"""
Business rules validation engine.
"""

from typing import Callable, List

import pandas as pd

from src.core.logging import get_logger
from src.pipelines.validation.report import ValidationReport

logger = get_logger(__name__)


class BusinessRule:
    def __init__(self, name: str, check_func: Callable[[pd.DataFrame], pd.Series], error_msg: str):
        self.name = name
        self.check_func = check_func
        self.error_msg = error_msg


class BusinessValidator:
    """Applies a configurable suite of business rules to the dataset."""

    def __init__(self, rules: List[BusinessRule]):
        self.rules = rules

    def validate(self, df: pd.DataFrame, report: ValidationReport) -> None:
        logger.info(f"Starting business validation with {len(self.rules)} rules...")
        
        # Boolean mask where True means the row is INVALID
        combined_failures = pd.Series(False, index=df.index)
        
        for rule in self.rules:
            try:
                # check_func returns a boolean series where True indicates a violation
                failures = rule.check_func(df)
                combined_failures = combined_failures | failures
                
                failure_count = int(failures.sum())
                if failure_count > 0:
                    report.add_warning(f"{rule.name}: {failure_count} violations ({rule.error_msg})")
                    report.business_rule_violations[rule.name] = f"{failure_count} violations"
                else:
                    report.add_passed(rule.name)
            except Exception as e:
                report.add_warning(f"Rule execution error for {rule.name}: {str(e)}")
                
        invalid_mask = combined_failures
        valid_mask = ~combined_failures
        
        # Record integer indices for easy retrieval
        # df.index isn't guaranteed to be 0-N integer indices, so we use positional indices
        import numpy as np
        positional_indices = np.arange(len(df))
        
        report.invalid_indices = positional_indices[invalid_mask].tolist()
        report.valid_indices = positional_indices[valid_mask].tolist()
        
        logger.info(f"Business validation complete. {len(report.invalid_indices)} rows rejected.")


def get_standard_loan_rules() -> List[BusinessRule]:
    """Returns standard business rules for the Lending platform."""
    return [
        BusinessRule(
            name="Positive Loan Amount",
            check_func=lambda df: (
                df["loan_amnt"] <= 0 if "loan_amnt" in df.columns else pd.Series(False, index=df.index)
            ),
            error_msg="Loan amount must be strictly positive.",
        ),
        BusinessRule(
            name="Valid Interest Rate",
            check_func=lambda df: (
                (df["int_rate"] < 0) | (df["int_rate"] > 50)
                if "int_rate" in df.columns
                else pd.Series(False, index=df.index)
            ),
            error_msg="Interest rate must be between 0 and 50.",
        ),
        BusinessRule(
            name="Valid Term",
            check_func=lambda df: (
                ~df["term"].isin([36, 60, "36 months", "60 months"])
                if "term" in df.columns
                else pd.Series(False, index=df.index)
            ),
            error_msg="Term must be 36 or 60 months.",
        ),
        BusinessRule(
            name="Positive Annual Income",
            check_func=lambda df: (
                df["annual_inc"] < 0 if "annual_inc" in df.columns else pd.Series(False, index=df.index)
            ),
            error_msg="Annual income cannot be negative.",
        ),
    ]
