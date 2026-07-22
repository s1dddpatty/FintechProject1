import time
from typing import Any

from fastapi import Request
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.logging import get_logger
from src.observability.metrics import (
    ACTIVE_REQUESTS,
    EXCEPTIONS_BY_TYPE,
    FAILED_REQUESTS,
    HTTP_REQUEST_COUNT,
    HTTP_REQUEST_DURATION,
)
from src.observability.tracing import get_correlation_id

logger = get_logger(__name__)

# Create the ASGI app for Prometheus metrics exposition
metrics_app = make_asgi_app()

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that instruments HTTP requests for observability.
    - Manages tracing (correlation_id)
    - Records Prometheus metrics (duration, count, active, failures)
    - Outputs structured access logs
    """
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Avoid instrumenting the metrics endpoint itself to prevent noise
        if request.url.path == "/metrics":
            return await call_next(request)

        # Ensure a correlation ID is generated/retrieved for this context
        request_id = get_correlation_id()
        start_time = time.time()
        
        ACTIVE_REQUESTS.inc()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            EXCEPTIONS_BY_TYPE.labels(exception_type=e.__class__.__name__).inc()
            logger.error(
                "Unhandled exception during request processing",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "processing_time": time.time() - start_time,
                },
                exc_info=True,
            )
            raise
        finally:
            ACTIVE_REQUESTS.dec()
            process_time = time.time() - start_time
            
            HTTP_REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(process_time)
            HTTP_REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code=status_code).inc()
            
            if status_code >= 400:
                FAILED_REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()

            # Structured access log for the request
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "processing_time": process_time,
                }
            )

        # Inject correlation ID and process time into headers for tracing
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response
