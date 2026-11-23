from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from src.api.dependencies import get_db
from src.pipelines.feature_engineering.service import FeatureEngineeringService
from src.pipelines.training.trainer import ModelTrainer
from src.pipelines.training.registry import ModelRegistry
from src.pipelines.prediction.portfolio import PortfolioScoringService
from src.core.logging import get_logger
import json
import os
from pathlib import Path

logger = get_logger(__name__)
router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# In-memory singletons for the service to retain state between runs
_ml_service = FeatureEngineeringService()
_portfolio_service = PortfolioScoringService()

@router.post("/features/generate")
def generate_features(db: Session = Depends(get_db)):
    """Runs the feature engineering pipeline and caches results in memory."""
    try:
        _ml_service.db_session = db
        summary = _ml_service.run_pipeline()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features/summary")
def get_features_summary():
    """Returns the metadata and summary of the engineered features."""
    summary = _ml_service.get_summary()
    if "error" in summary:
        raise HTTPException(status_code=400, detail=summary["error"])
    return summary

@router.get("/features/preview")
def get_features_preview():
    """Returns a preview of the engineered feature matrix."""
    preview = _ml_service.get_preview()
    if "error" in preview:
        raise HTTPException(status_code=400, detail=preview["error"])
    return preview

from src.pipelines.training.trainer import ModelTrainer
from src.pipelines.training.registry import ModelRegistry
import json
from pathlib import Path

@router.post("/train")
def train_model(db: Session = Depends(get_db)):
    """Trains ML models using the feature engineering pipeline and saves the best one."""
    try:
        trainer = ModelTrainer(db)
        metadata = trainer.train()
        return metadata
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
def list_models():
    """Lists trained models."""
    artifacts_dir = Path("artifacts/models")
    if not artifacts_dir.exists():
        return {"models": []}
        
    models = []
    metadata_path = artifacts_dir / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            data = json.load(f)
            models.append(data)
            
    return {"models": models}

@router.get("/models/latest")
def get_latest_model():
    """Returns metadata for the latest trained model."""
    artifacts_dir = Path("artifacts/models")
    metadata_path = artifacts_dir / "metadata.json"
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="No trained models found.")
        
    with open(metadata_path, "r") as f:
        data = json.load(f)
        
    return data

@router.post("/portfolio/score")
async def score_portfolio(file: UploadFile = File(...)):
    """Runs the prediction pipeline against a CSV of new applications and returns analytics."""
    logger.info(f"Received Portfolio Scoring request for file: {file.filename}")
    try:
        results = await _portfolio_service.score_portfolio(file)
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/download/{session_id}")
async def download_portfolio(session_id: str):
    """Downloads the scored CSV for a given session."""
    try:
        csv_path = _portfolio_service.get_scored_csv_path(session_id)
        return FileResponse(
            path=csv_path,
            filename=f"scored_portfolio_{session_id[:8]}.csv",
            media_type="text/csv"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/download-tableau/{session_id}")
async def download_tableau_portfolio(session_id: str):
    """Downloads a Tableau / PowerBI optimized dataset with dimensions and measures."""
    try:
        csv_path = _portfolio_service.get_tableau_csv_path(session_id)
        return FileResponse(
            path=csv_path,
            filename=f"tableau_credit_risk_{session_id[:8]}.csv",
            media_type="text/csv"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download Tableau portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
