from src.core.exceptions import FintechBaseException


class MLError(FintechBaseException):
    """Base exception for ML platform."""

    pass


class TrainingError(MLError):
    pass


class PredictionError(MLError):
    pass


class RegistryError(MLError):
    pass


class EvaluationError(MLError):
    pass


class ExplainabilityError(MLError):
    pass
