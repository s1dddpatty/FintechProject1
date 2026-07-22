import time

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import FintechBaseException
from src.core.logging import get_logger
from src.observability.metrics import EXCEPTIONS_BY_TYPE

logger = get_logger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    EXCEPTIONS_BY_TYPE.labels(exception_type=exc.__class__.__name__).inc()
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected system error occurred.",
            "timestamp": time.time(),
        },
    )


async def fintech_exception_handler(request: Request, exc: FintechBaseException):
    EXCEPTIONS_BY_TYPE.labels(exception_type=exc.__class__.__name__).inc()
    logger.warning(f"Domain exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=400, content={"error_code": exc.__class__.__name__, "message": str(exc), "timestamp": time.time()}
    )
