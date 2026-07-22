import time
from typing import Dict, List

from pydantic import BaseModel

from src.core.logging import get_logger

from .dataset import MLDataset
from .evaluator import ModelEvaluator
from .explainability import ModelExplainer
from .metrics import EvaluationMetrics
from .registry import ModelRegistry
from .trainer import ModelTrainer

logger = get_logger(__name__)


class TrainingReport(BaseModel):
    best_model_id: str
    best_algorithm: str
    metrics: EvaluationMetrics
    feature_importance: Dict[str, float]
    training_duration_seconds: float


class MachineLearningPipeline:
    """Orchestrates algorithmic ML training, evaluation, comparison, and persistence."""

    def __init__(
        self, trainer: ModelTrainer, evaluator: ModelEvaluator, registry: ModelRegistry, explainer: ModelExplainer
    ):
        self.trainer = trainer
        self.evaluator = evaluator
        self.registry = registry
        self.explainer = explainer

    def run(self, train_data: MLDataset, test_data: MLDataset, algorithms: List[str]) -> TrainingReport:
        start_time = time.time()
        logger.info(f"Starting ML Pipeline orchestration. Requested algorithms: {algorithms}")

        trained_models = {}
        evaluations = {}

        # Train and Evaluate multiple models
        for algo in algorithms:
            model = self.trainer.train(algo, train_data)
            trained_models[algo] = model

            metrics = self.evaluator.evaluate(model, test_data)
            evaluations[algo] = metrics

        # Compare and Select Best Model
        comparison = self.evaluator.compare_models(evaluations)
        best_algo = comparison.best_model_name
        best_model = trained_models[best_algo]
        best_metrics = evaluations[best_algo]

        logger.info(f"Comparison complete. Best model identified: {best_algo} with ROC AUC {best_metrics.roc_auc:.4f}")

        # Persist Best Model
        model_id = self.registry.save_model(
            model=best_model,
            algorithm=best_algo,
            features=train_data.X.columns.tolist(),
            params=best_model.get_params(),
            metrics=best_metrics,
        )

        # Explain Top Features
        importances = self.explainer.get_feature_importance(best_model, test_data)

        duration = time.time() - start_time
        logger.info(f"ML Pipeline run completed in {duration:.2f} seconds.")

        return TrainingReport(
            best_model_id=model_id,
            best_algorithm=best_algo,
            metrics=best_metrics,
            feature_importance=importances,
            training_duration_seconds=duration,
        )
