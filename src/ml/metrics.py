from typing import Any, Dict, List

from pydantic import BaseModel


class EvaluationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float = 0.0
    confusion_matrix: List[List[int]]
    classification_report: Dict[str, Any]


class CrossValidationMetrics(BaseModel):
    mean_accuracy: float
    std_accuracy: float
    scores: List[float]


class ModelComparison(BaseModel):
    best_model_name: str
    comparison_table: Dict[str, EvaluationMetrics]
