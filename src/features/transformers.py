import numpy as np
import pandas as pd

from src.core.logging import get_logger

from .exceptions import TransformationError

logger = get_logger(__name__)


class DerivedFeaturesTransformer:
    """Computes derived financial features from raw columns."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Applying derived feature transformations...")
        try:
            df = df.copy()
            df = self._loan_to_income(df)
            df = self._interest_burden(df)
            df = self._log_transforms(df)
            return df
        except Exception as e:
            raise TransformationError(f"Derived feature transformation failed: {e}")

    def _loan_to_income(self, df: pd.DataFrame) -> pd.DataFrame:
        if "loan_amnt" in df.columns and "annual_inc" in df.columns:
            # Add small epsilon to prevent division by zero
            df["loan_to_income_ratio"] = df["loan_amnt"] / (df["annual_inc"] + 1.0)
        return df

    def _interest_burden(self, df: pd.DataFrame) -> pd.DataFrame:
        # Simplistic burden proxy: interest_rate * loan_amnt
        if "loan_amnt" in df.columns and "int_rate" in df.columns:
            df["interest_burden_proxy"] = df["loan_amnt"] * (df["int_rate"] / 100.0)
        return df

    def _log_transforms(self, df: pd.DataFrame) -> pd.DataFrame:
        # Standard to log-transform highly skewed features like income
        if "annual_inc" in df.columns:
            df["annual_inc_log"] = np.log1p(df["annual_inc"])
        if "loan_amnt" in df.columns:
            df["loan_amnt_log"] = np.log1p(df["loan_amnt"])
        return df
