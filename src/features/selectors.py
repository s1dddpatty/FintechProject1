import numpy as np
import pandas as pd
from sklearn.feature_selection import VarianceThreshold

from src.core.logging import get_logger

from .exceptions import SelectionError

logger = get_logger(__name__)


class FeatureSelector:
    """Removes low-variance or highly correlated features."""

    def __init__(self, variance_threshold: float = 0.01, correlation_threshold: float = 0.95):
        self.variance_threshold = variance_threshold
        self.correlation_threshold = correlation_threshold
        self.selector = VarianceThreshold(threshold=self.variance_threshold)
        self.selector.set_output(transform="pandas")
        self.features_to_drop = []
        self._is_fit = False

    def fit(self, df: pd.DataFrame):
        try:
            numeric_df = df.select_dtypes(include="number")
            # 1. Variance Check
            self.selector.fit(numeric_df)
            retained_vars = set(self.selector.get_feature_names_out())
            all_vars = set(numeric_df.columns)
            low_var_cols = list(all_vars - retained_vars)

            # 2. Correlation Check
            corr_matrix = numeric_df.corr().abs()
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            high_corr_cols = [column for column in upper.columns if any(upper[column] > self.correlation_threshold)]

            self.features_to_drop = list(set(low_var_cols + high_corr_cols))
            self._is_fit = True
        except Exception as e:
            raise SelectionError(f"Feature selector fitting failed: {e}")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._is_fit:
            raise SelectionError("Selector must be fit before transforming.")

        logger.info(f"Dropping {len(self.features_to_drop)} features during selection phase.")
        try:
            return df.drop(columns=[col for col in self.features_to_drop if col in df.columns])
        except Exception as e:
            raise SelectionError(f"Feature selection transformation failed: {e}")
