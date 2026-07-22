import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from src.core.logging import get_logger

from .exceptions import EncodingError

logger = get_logger(__name__)


class CategoricalEncoder:
    """Applies robust categorical encoding mapping text to numbers."""

    def __init__(self, ordinal_cols=None, onehot_cols=None):
        self.ordinal_cols = ordinal_cols or []
        self.onehot_cols = onehot_cols or []
        self.ordinal_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        self.onehot_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        self._is_fit = False

    def fit(self, df: pd.DataFrame):
        try:
            if self.ordinal_cols:
                self.ordinal_encoder.fit(df[self.ordinal_cols])
            if self.onehot_cols:
                self.onehot_encoder.set_output(transform="pandas")
                self.onehot_encoder.fit(df[self.onehot_cols])
            self._is_fit = True
        except Exception as e:
            raise EncodingError(f"Encoder fitting failed: {e}")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._is_fit:
            raise EncodingError("Encoder must be fit before calling transform.")

        df_out = df.copy()
        logger.info("Applying categorical encodings...")
        try:
            if self.ordinal_cols:
                df_out[self.ordinal_cols] = self.ordinal_encoder.transform(df_out[self.ordinal_cols])

            if self.onehot_cols:
                encoded_dfs = self.onehot_encoder.transform(df_out[self.onehot_cols])
                # Drop original categorical columns dynamically
                df_out.drop(columns=self.onehot_cols, inplace=True)
                df_out = pd.concat([df_out, encoded_dfs], axis=1)

            return df_out
        except Exception as e:
            raise EncodingError(f"Encoding transformation failed: {e}")
