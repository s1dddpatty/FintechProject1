import time
from functools import wraps
from typing import Any, Callable

from prometheus_client import Counter, Gauge, Histogram

# --- HTTP Metrics ---
HTTP_REQUEST_COUNT = Counter(
    "http_request_count",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)
ACTIVE_REQUESTS = Gauge(
    "active_requests",
    "Number of active HTTP requests"
)
FAILED_REQUESTS = Counter(
    "failed_requests_total",
    "Total number of failed HTTP requests (status >= 400)",
    ["method", "endpoint"]
)

# --- Business Metrics ---
PREDICTION_COUNT = Counter(
    "prediction_count_total",
    "Total number of predictions made"
)
PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Prediction latency in seconds"
)
PREDICTION_FAILURES = Counter(
    "prediction_failures_total",
    "Total number of prediction failures"
)

INGESTION_COUNT = Counter(
    "ingestion_count_total",
    "Total number of ingestion jobs executed"
)
INGESTION_DURATION = Histogram(
    "ingestion_duration_seconds",
    "Ingestion job duration in seconds"
)

VALIDATION_FAILURES = Counter(
    "validation_failures_total",
    "Total number of validation failures"
)

# --- Database & Error Metrics ---
DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"]
)
EXCEPTIONS_BY_TYPE = Counter(
    "exceptions_total",
    "Total exceptions raised, by type",
    ["exception_type"]
)

# --- Decorators for Service Layer Instrumentation ---

def track_prediction(func: Callable) -> Callable:
    """Decorator to track prediction latency, count, and failures."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            PREDICTION_COUNT.inc()
            return result
        except Exception as e:
            PREDICTION_FAILURES.inc()
            EXCEPTIONS_BY_TYPE.labels(exception_type=e.__class__.__name__).inc()
            raise
        finally:
            PREDICTION_LATENCY.observe(time.time() - start_time)
    return wrapper

def track_ingestion(func: Callable) -> Callable:
    """Decorator to track ingestion duration and count."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            INGESTION_COUNT.inc()
            return result
        except Exception as e:
            EXCEPTIONS_BY_TYPE.labels(exception_type=e.__class__.__name__).inc()
            raise
        finally:
            INGESTION_DURATION.observe(time.time() - start_time)
    return wrapper

def track_db_query(operation: str) -> Callable:
    """Decorator to track database query duration."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                EXCEPTIONS_BY_TYPE.labels(exception_type=e.__class__.__name__).inc()
                raise
            finally:
                DB_QUERY_DURATION.labels(operation=operation).observe(time.time() - start_time)
        return wrapper
    return decorator
