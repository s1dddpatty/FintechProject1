import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_model_registry
from src.api.schemas import HealthResponse
from src.ml.registry import ModelRegistry

router = APIRouter(prefix="/health", tags=["System"])


@router.get("", response_model=HealthResponse)
def check_health(db: Session = Depends(get_db), registry: ModelRegistry = Depends(get_model_registry)):
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

    return HealthResponse(
        status="active", database=db_status, registry=reg_status, version="1.0.0", timestamp=time.time()
    )
