from typing import Any, Dict

from sklearn.inspection import permutation_importance

from src.core.logging import get_logger

from .dataset import MLDataset
from .exceptions import ExplainabilityError

logger = get_logger(__name__)


class ModelExplainer:
    """Calculates global feature importance using agnostic permutation checks."""

    def get_feature_importance(self, model: Any, dataset: MLDataset, random_state: int = 42) -> Dict[str, float]:
        logger.info("Calculating permutation feature importance...")
        try:
            result = permutation_importance(
                model, dataset.X, dataset.y, n_repeats=5, random_state=random_state, n_jobs=-1
            )

            importances = result.importances_mean
            importance_dict = {col: float(imp) for col, imp in zip(dataset.X.columns, importances)}

            # Sort descending for top-contributing insights
            sorted_importance = dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))
            logger.info("Feature importance calculated successfully.")
            return sorted_importance
        except Exception as e:
            raise ExplainabilityError(f"Failed to calculate feature importance: {e}")
