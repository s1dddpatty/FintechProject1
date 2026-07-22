"""
Ingestion-specific exceptions.
"""

from src.core.exceptions import FintechBaseException


class IngestionError(FintechBaseException):
    """Base class for ingestion errors."""

    pass


class DataReaderError(IngestionError):
    """Raised when data reading from a source fails."""

    pass


class DataCleaningError(IngestionError):
    """Raised when cleaning operations fail."""

    pass


class DataNormalizationError(IngestionError):
    """Raised when data normalization fails."""

    pass
