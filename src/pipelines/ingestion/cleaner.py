"""
Data cleaning engine.
"""

import numpy as np
import pandas as pd

from src.core.logging import get_logger

from .exceptions import DataCleaningError

logger = get_logger(__name__)


class DataCleaner:
    """Performs generic cleaning operations without enforcing domain logic."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data cleaning...")
        try:
            df = df.copy()
            df = self._apply_column_aliases(df)
            df = self._normalize_dates(df)
            df = self._drop_empty_rows(df)
            df = self._remove_duplicates(df)
            df = self._trim_whitespace(df)
            df = self._normalize_nulls(df)
            logger.info("Data cleaning completed successfully.")
            return df
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            raise DataCleaningError(f"Cleaning error: {e}")

    def _apply_column_aliases(self, df: pd.DataFrame) -> pd.DataFrame:
        alias_map = {
            "loan_amount": "loan_amnt",
            "funded_amount": "loan_amnt",
            "income": "annual_inc",
            "annual_income": "annual_inc",
            "interest_rate": "int_rate",
            "state": "addr_state",
            "memberid": "member_id",
            "loan_status": "loan_status",
        }
        # Normalize incoming columns to lower case for mapping
        lower_cols = {col: str(col).lower().strip() for col in df.columns}
        df.rename(columns=lower_cols, inplace=True)
        
        # Apply aliases
        rename_map = {col: alias_map[col] for col in df.columns if col in alias_map}
        df.rename(columns=rename_map, inplace=True)
        logger.info(f"Applied column aliases: {rename_map}")
        return df

    def _normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        date_cols = ["issue_d"]
        for col in date_cols:
            if col in df.columns:
                # Convert "Dec-2011" or similar to standard datetime, then string YYYY-MM-DD
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
        return df

    def _drop_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        original_len = len(df)
        df.dropna(how="all", inplace=True)
        dropped = original_len - len(df)
        if dropped > 0:
            logger.info(f"Dropped {dropped} completely empty rows.")
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        original_len = len(df)
        df.drop_duplicates(inplace=True)
        dropped = original_len - len(df)
        if dropped > 0:
            logger.info(f"Dropped {dropped} duplicate rows.")
        return df

    def _trim_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        str_cols = df.select_dtypes(include=["object"]).columns
        for col in str_cols:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        return df

    def _normalize_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        null_representations = ["", "NA", "N/A", "null", "NULL", "none", "None", np.nan]
        df.replace(null_representations, np.nan, inplace=True)
        return df
