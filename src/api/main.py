from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from src.api.exceptions import fintech_exception_handler, global_exception_handler
from src.api.routers import analytics, ingestion, models, prediction, ml, admin
from src.core.exceptions import FintechBaseException
from src.core.logging import get_logger
from src.observability.health import router as health_router
from src.observability.instrumentation import ObservabilityMiddleware, metrics_app
from src.observability.logging import setup_structured_logging

logger = get_logger(__name__)

app = FastAPI(
    title="Fintech Analytics Platform API",
    description="Production REST Gateway Orchestrating the Lending Risk and Analytics Pipelines",
    version="1.0.0",
)

# Application Middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ObservabilityMiddleware)

# Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(FintechBaseException, fintech_exception_handler)

# Routers
app.include_router(health_router)
app.mount("/metrics", metrics_app)
app.include_router(ingestion.router)
app.include_router(analytics.router)
app.include_router(models.router)
app.include_router(prediction.router)
app.include_router(ml.router)
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event():
    setup_structured_logging(logger)
    logger.info("Starting Fintech Analytics API Server...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Fintech Analytics API Server...")
