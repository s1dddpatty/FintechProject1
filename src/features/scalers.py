from typing import List

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

from src.core.logging import get_logger

from .exceptions import ScalingError

logger = get_logger(__name__)


class FeatureScaler:
    """Standardizes dataset distributions."""

    def __init__(self, method: str = "standard", columns: List[str] = None):
        self.method = method.lower()
        self.columns = columns or []

        if self.method == "standard":
            self.scaler = StandardScaler()
        elif self.method == "robust":
            self.scaler = RobustScaler()
        elif self.method == "minmax":
            self.scaler = MinMaxScaler()
        else:
            raise ScalingError(f"Unsupported scaling method: {self.method}")

        self.scaler.set_output(transform="pandas")
        self._is_fit = False

    def fit(self, df: pd.DataFrame):
        if not self.columns:
            # Auto-detect numeric
            self.columns = df.select_dtypes(include=[np.number]).columns.tolist()

        try:
            self.scaler.fit(df[self.columns])
            self._is_fit = True
        except Exception as e:
            raise ScalingError(f"Scaler fitting failed: {e}")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._is_fit:
            raise ScalingError("Scaler must be fit before transforming.")

        df_out = df.copy()
        logger.info(f"Applying {self.method} scaling to {len(self.columns)} columns...")
        try:
            scaled_features = self.scaler.transform(df_out[self.columns])
            df_out[self.columns] = scaled_features
            return df_out
        except Exception as e:
            raise ScalingError(f"Scaling transformation failed: {e}")
