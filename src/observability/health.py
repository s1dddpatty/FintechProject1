import os
import shutil
import time

import psutil
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_model_registry
from src.core.config import PROJECT_ROOT
from src.ml.registry import ModelRegistry

# We will mount this router instead of the original health router.
router = APIRouter(tags=["Observability"])

START_TIME = time.time()
VERSION = "1.0.0"

@router.get("/health")
def health_check(db: Session = Depends(get_db), registry: ModelRegistry = Depends(get_model_registry)) -> dict:
    """Comprehensive health check including system stats and dependencies."""
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"

    reg_status = "ok"
    try:
        if not registry.registry_dir.exists():
            reg_status = "missing_directory"
    except Exception:
        reg_status = "error"

    # Disk usage for the project root
    total, used, free = shutil.disk_usage(PROJECT_ROOT)
    disk_usage_percent = (used / total) * 100

    # Memory usage via psutil
    memory_info = psutil.virtual_memory()

    return {
        "status": "healthy" if db_status == "ok" and reg_status == "ok" else "degraded",
        "version": VERSION,
        "uptime_seconds": time.time() - START_TIME,
        "database": db_status,
        "registry": reg_status,
        "disk_usage_percent": round(disk_usage_percent, 2),
        "memory_usage_percent": memory_info.percent,
        "build": {
            "git_commit": os.getenv("GIT_COMMIT", "unknown"),
            "build_time": os.getenv("BUILD_TIME", "unknown"),
            "python_version": os.getenv("PYTHON_VERSION", "unknown"),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    }

@router.get("/live")
def liveness_check() -> dict:
    """Simple lightweight liveness probe."""
    return {"status": "alive"}

@router.get("/ready")
def readiness_check(db: Session = Depends(get_db), registry: ModelRegistry = Depends(get_model_registry)) -> dict:
    """Readiness probe checking backing services connectivity."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "not_ready", "reason": f"Database unavailable: {e}"}

    if not registry.registry_dir.exists():
        return {"status": "not_ready", "reason": "Model registry directory missing"}

    return {"status": "ready"}
