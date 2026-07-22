"""
Validation-specific exceptions.
"""

from src.core.exceptions import FintechBaseException


class ValidationError(FintechBaseException):
    """Base class for validation errors."""

    pass


class SchemaValidationError(ValidationError):
    """Raised when the dataset schema is invalid."""

    pass


class BusinessRuleValidationError(ValidationError):
    """Raised when business logic rules are violated."""

    pass


class QualityValidationError(ValidationError):
    """Raised when data quality thresholds are not met."""

    pass
