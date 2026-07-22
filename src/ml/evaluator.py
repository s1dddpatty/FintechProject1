from typing import Any, Dict

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score

from src.core.logging import get_logger

from .dataset import MLDataset
from .exceptions import EvaluationError
from .metrics import CrossValidationMetrics, EvaluationMetrics, ModelComparison

logger = get_logger(__name__)


class ModelEvaluator:
    """Evaluates and compares trained models."""

    def evaluate(self, model: Any, dataset: MLDataset) -> EvaluationMetrics:
        logger.info("Evaluating model performance...")
        try:
            preds = model.predict(dataset.X)
            probs = model.predict_proba(dataset.X)[:, 1] if hasattr(model, "predict_proba") else None

            y_true = dataset.y

            acc = float(accuracy_score(y_true, preds))
            prec = float(precision_score(y_true, preds, zero_division=0))
            rec = float(recall_score(y_true, preds, zero_division=0))
            f1 = float(f1_score(y_true, preds, zero_division=0))
            roc = float(roc_auc_score(y_true, probs)) if probs is not None else 0.0
            cm = confusion_matrix(y_true, preds).tolist()
            report = classification_report(y_true, preds, output_dict=True, zero_division=0)

            metrics = EvaluationMetrics(
                accuracy=acc,
                precision=prec,
                recall=rec,
                f1_score=f1,
                roc_auc=roc,
                confusion_matrix=cm,
                classification_report=report,
            )
            logger.info(f"Evaluation complete. Accuracy: {acc:.4f}, ROC AUC: {roc:.4f}")
            return metrics
        except Exception as e:
            raise EvaluationError(f"Evaluation failed: {e}")

    def cross_validate(self, model: Any, dataset: MLDataset, cv: int = 5) -> CrossValidationMetrics:
        try:
            scores = cross_val_score(model, dataset.X, dataset.y, cv=cv, scoring="accuracy")
            return CrossValidationMetrics(
                mean_accuracy=float(scores.mean()), std_accuracy=float(scores.std()), scores=scores.tolist()
            )
        except Exception as e:
            raise EvaluationError(f"Cross validation failed: {e}")

    def compare_models(self, evaluated_models: Dict[str, EvaluationMetrics]) -> ModelComparison:
        logger.info("Comparing models...")
        best_model = None
        best_score = -1.0

        for name, metrics in evaluated_models.items():
            if metrics.roc_auc > best_score:
                best_score = metrics.roc_auc
                best_model = name

        if best_model is None:
            # Fallback to accuracy if roc_auc not available
            for name, metrics in evaluated_models.items():
                if metrics.accuracy > best_score:
                    best_score = metrics.accuracy
                    best_model = name

        return ModelComparison(best_model_name=best_model, comparison_table=evaluated_models)
