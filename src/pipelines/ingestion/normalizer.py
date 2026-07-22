"""
Data normalization engine.
"""

from typing import List

import pandas as pd

from src.core.logging import get_logger

from .exceptions import DataNormalizationError

logger = get_logger(__name__)


class DataNormalizer:
    """Normalizes formatting of strings, dates, currencies, and booleans."""

    def __init__(
        self, date_columns: List[str] = None, bool_columns: List[str] = None, currency_columns: List[str] = None
    ):
        self.date_columns = date_columns or []
        self.bool_columns = bool_columns or []
        self.currency_columns = currency_columns or []

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data normalization...")
        try:
            df = df.copy()
            df = self._normalize_column_names(df)
            df = self._normalize_dates(df)
            df = self._normalize_booleans(df)
            df = self._normalize_currencies(df)
            logger.info("Data normalization completed successfully.")
            return df
        except Exception as e:
            logger.error(f"Data normalization failed: {e}")
            raise DataNormalizationError(f"Normalization error: {e}")

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [str(col).strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns]
        return df

    def _normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    def _normalize_booleans(self, df: pd.DataFrame) -> pd.DataFrame:
        bool_map = {
            "true": True,
            "t": True,
            "yes": True,
            "y": True,
            "1": True,
            1: True,
            "false": False,
            "f": False,
            "no": False,
            "n": False,
            "0": False,
            0: False,
        }
        for col in self.bool_columns:
            if col in df.columns:
                df[col] = df[col].map(lambda x: bool_map.get(str(x).strip().lower(), x))
        return df

    def _normalize_currencies(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.currency_columns:
            if col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.replace(r"[\$,]", "", regex=True)
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
