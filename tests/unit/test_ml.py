import shutil
import tempfile

import numpy as np
import pandas as pd
import pytest

from src.ml.dataset import MLDataset
from src.ml.evaluator import ModelEvaluator
from src.ml.explainability import ModelExplainer
from src.ml.pipeline import MachineLearningPipeline
from src.ml.predictor import ModelPredictor
from src.ml.registry import ModelRegistry
from src.ml.trainer import ModelTrainer


@pytest.fixture
def dummy_data():
    np.random.seed(42)
    X = pd.DataFrame({"feat1": np.random.rand(100), "feat2": np.random.rand(100) * 10})
    y = pd.Series(np.random.randint(0, 2, size=100))

    train_ds = MLDataset(X=X.iloc[:80], y=y.iloc[:80])
    test_ds = MLDataset(X=X.iloc[80:], y=y.iloc[80:])
    return train_ds, test_ds


@pytest.fixture
def temp_registry():
    d = tempfile.mkdtemp()
    yield ModelRegistry(registry_dir=d)
    shutil.rmtree(d)


def test_trainer_and_evaluator(dummy_data):
    train_ds, test_ds = dummy_data
    trainer = ModelTrainer()
    model = trainer.train("logistic_regression", train_ds)
    assert model is not None

    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate(model, test_ds)

    assert metrics.accuracy >= 0.0
    assert metrics.roc_auc >= 0.0
    assert "precision" in metrics.model_dump()

    cv_metrics = evaluator.cross_validate(model, train_ds, cv=3)
    assert cv_metrics.mean_accuracy > 0


def test_registry_and_predictor(dummy_data, temp_registry):
    train_ds, test_ds = dummy_data
    trainer = ModelTrainer()
    model = trainer.train("random_forest", train_ds)

    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate(model, test_ds)

    model_id = temp_registry.save_model(model, "random_forest", train_ds.X.columns.tolist(), {}, metrics)
    assert model_id is not None

    predictor = ModelPredictor(temp_registry)
    preds, probs = predictor.predict(model_id, test_ds)

    assert len(preds) == 20
    assert len(probs) == 20


def test_explainer(dummy_data):
    train_ds, test_ds = dummy_data
    trainer = ModelTrainer()
    model = trainer.train("gradient_boosting", train_ds)

    explainer = ModelExplainer()
    importances = explainer.get_feature_importance(model, test_ds)

    assert "feat1" in importances
    assert "feat2" in importances


def test_ml_pipeline(dummy_data, temp_registry):
    train_ds, test_ds = dummy_data
    pipeline = MachineLearningPipeline(ModelTrainer(), ModelEvaluator(), temp_registry, ModelExplainer())

    report = pipeline.run(train_ds, test_ds, ["logistic_regression", "random_forest"])
    assert report.best_algorithm in ["logistic_regression", "random_forest"]
    assert report.best_model_id is not None
    assert len(report.feature_importance) == 2
