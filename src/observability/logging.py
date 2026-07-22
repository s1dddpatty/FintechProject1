import json
import logging
from typing import Any, Dict

from src.observability.tracing import get_correlation_id

class StructuredJsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for structured logging.
    Injects the correlation ID from contextvars.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_correlation_id(),
        }

        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "processing_time"):
            log_record["processing_time"] = record.processing_time
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_structured_logging(logger: logging.Logger) -> None:
    """Replaces standard formatters with StructuredJsonFormatter on the given logger."""
    formatter = StructuredJsonFormatter()
    for handler in logger.handlers:
        handler.setFormatter(formatter)
