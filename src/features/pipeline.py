from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from src.core.logging import get_logger

from .encoders import CategoricalEncoder
from .feature_store import FeatureMetadata, FeatureStoreRegistry
from .scalers import FeatureScaler
from .selectors import FeatureSelector
from .transformers import DerivedFeaturesTransformer

logger = get_logger(__name__)


class FeatureEngineeringPipeline:
    """Orchestrates derivation, encoding, scaling, and feature selection."""

    def __init__(
        self,
        transformer: DerivedFeaturesTransformer,
        encoder: CategoricalEncoder,
        scaler: FeatureScaler,
        selector: FeatureSelector,
        store: FeatureStoreRegistry,
    ):
        self.transformer = transformer
        self.encoder = encoder
        self.scaler = scaler
        self.selector = selector
        self.store = store
        self.history = []

    def fit_transform(
        self, df: pd.DataFrame, target_col: str, test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        logger.info("Starting feature engineering pipeline...")

        # 1. Derive
        df_derived = self.transformer.transform(df)
        self.history.append("DerivedFeaturesTransformer applied")

        # Train/Test Split BEFORE fit to prevent data leakage!
        y = df_derived[target_col] if target_col in df_derived.columns else None
        X = df_derived.drop(columns=[target_col]) if target_col in df_derived.columns else df_derived

        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        else:
            X_train = X
            X_test = pd.DataFrame()
            y_train, y_test = None, None

        # 2. Encode
        self.encoder.fit(X_train)
        X_train_enc = self.encoder.transform(X_train)
        X_test_enc = self.encoder.transform(X_test) if not X_test.empty else X_test
        self.history.append("CategoricalEncoder fit and applied")

        # 3. Scale
        self.scaler.fit(X_train_enc)
        X_train_scl = self.scaler.transform(X_train_enc)
        X_test_scl = self.scaler.transform(X_test_enc) if not X_test.empty else X_test
        self.history.append(f"FeatureScaler ({self.scaler.method}) fit and applied")

        # 4. Select
        self.selector.fit(X_train_scl)
        X_train_final = self.selector.transform(X_train_scl)
        X_test_final = self.selector.transform(X_test_scl) if not X_test.empty else X_test
        self.history.append("FeatureSelector fit and applied")

        # Capture Metadata
        final_columns = X_train_final.columns.tolist()
        metadata = FeatureMetadata(
            feature_names=final_columns, num_features=len(final_columns), transformation_history=self.history
        )

        # Store securely
        self.store.save(X_train_final, X_test_final, metadata, y_train, y_test)
        logger.info(f"Feature engineering complete. {len(final_columns)} features retained.")

        return X_train_final, X_test_final
