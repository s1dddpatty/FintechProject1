import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.api.schemas import ResetDatasetRequest, ResetDatasetResponse
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/reset-dataset", response_model=ResetDatasetResponse)
async def reset_dataset(request: ResetDatasetRequest, db: Session = Depends(get_db)):
    logger.warning(f"Resetting dataset with options: {request.dict()}")

    try:
        # 1. Count rows before deletion
        loans_count = db.execute(text("SELECT COUNT(*) FROM loans")).scalar()
        predictions_count = db.execute(text("SELECT COUNT(*) FROM predictions")).scalar()
        payments_count = db.execute(text("SELECT COUNT(*) FROM payments")).scalar()

        if request.dry_run:
            logger.info("Dry run specified. Skipping deletion.")
            return ResetDatasetResponse(
                loans_deleted=loans_count,
                predictions_deleted=predictions_count,
                payments_deleted=payments_count,
                models_deleted=not request.keep_models,
                database_ready=True,
                message="Dry run complete. No data modified."
            )

        # 2. Truncate tables
        logger.warning("Truncating payments, predictions, and loans CASCADE...")
        db.execute(text("TRUNCATE payments, predictions, loans CASCADE;"))
        db.commit()

        # 3. Handle models directory
        models_deleted = False
        if not request.keep_models:
            models_dir = Path("artifacts/models")
            if models_dir.exists():
                logger.warning(f"Deleting model artifacts at {models_dir}...")
                for item in models_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                models_deleted = True

        return ResetDatasetResponse(
            loans_deleted=loans_count,
            predictions_deleted=predictions_count,
            payments_deleted=payments_count,
            models_deleted=models_deleted,
            database_ready=True,
            message="Dataset successfully reset."
        )

    except Exception as e:
        logger.error(f"Failed to reset dataset: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
