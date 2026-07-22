from typing import Any, Dict

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.core.logging import get_logger

from .dataset import MLDataset
from .exceptions import TrainingError

logger = get_logger(__name__)


class ModelTrainer:
    """Trains scikit-learn compatible classification models."""

    SUPPORTED_MODELS = {
        "logistic_regression": LogisticRegression,
        "random_forest": RandomForestClassifier,
        "gradient_boosting": GradientBoostingClassifier,
    }

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def train(self, algorithm: str, dataset: MLDataset, hyperparameters: Dict[str, Any] = None) -> Any:
        logger.info(f"Initiating training for algorithm: {algorithm}")
        if algorithm not in self.SUPPORTED_MODELS:
            raise TrainingError(f"Unsupported algorithm: {algorithm}. Supported: {list(self.SUPPORTED_MODELS.keys())}")

        params = hyperparameters or {}
        # inject random state if applicable for reproducibility
        if algorithm in ["random_forest", "gradient_boosting", "logistic_regression"]:
            params["random_state"] = params.get("random_state", self.random_state)

        try:
            model_class = self.SUPPORTED_MODELS[algorithm]
            model = model_class(**params)
            model.fit(dataset.X, dataset.y)
            logger.info(f"Successfully trained {algorithm}.")
            return model
        except Exception as e:
            logger.error(f"Training failed for {algorithm}: {e}")
            raise TrainingError(f"Model training failed: {e}")
