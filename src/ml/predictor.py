from typing import Tuple

import pandas as pd

from src.core.logging import get_logger
from src.observability.metrics import track_prediction

from .dataset import MLDataset
from .exceptions import PredictionError
from .registry import ModelRegistry

logger = get_logger(__name__)


class ModelPredictor:
    """Predictor engine loading verified models dynamically."""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    @track_prediction
    def predict(self, model_id: str, dataset: MLDataset) -> Tuple[pd.Series, pd.Series]:
        logger.info(f"Loading model {model_id} from registry for inference...")
        try:
            model = self.registry.load_model(model_id)
            metadata = self.registry.load_metadata(model_id)

            # Ensure runtime features exactly match training features
            missing_features = [f for f in metadata.feature_list if f not in dataset.X.columns]
            if missing_features:
                raise PredictionError(f"Prediction dataset missing required features: {missing_features}")

            # Align dataframe identically to the training structure
            X_aligned = dataset.X[metadata.feature_list]

            logger.info("Generating predictions...")
            preds = model.predict(X_aligned)
            probs = model.predict_proba(X_aligned)[:, 1] if hasattr(model, "predict_proba") else preds

            return pd.Series(preds), pd.Series(probs)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise PredictionError(f"Prediction execution failed: {e}")
