from src.core.exceptions import FintechBaseException


class LoadingError(FintechBaseException):
    """Base class for loading/persistence errors."""

    pass


class DataMappingError(LoadingError):
    """Raised when converting pandas rows to ORM models fails."""

    pass


class BatchInsertError(LoadingError):
    """Raised when a bulk insert database operation fails and rolls back."""

    pass
