from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from src.pipelines.ingestion.universal_cleaner import UniversalCleaningPipeline
from src.services.llm import LLMService
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Data Pipeline & LLM Audit"])

@router.post("/clean-and-engineer")
async def clean_and_engineer_dataset(file: UploadFile = File(...)):
    """
    Ingests any raw/messy CSV dataset, executes automated schema normalization,
    type sanitization, advanced financial feature engineering, quality scoring,
    and returns an AI-generated Data Transformation Audit Memorandum via local Ollama.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported for pipeline processing.")

    pipeline = UniversalCleaningPipeline()
    try:
        result = await pipeline.process_dataset(file.file, file.filename)
        return result
    except Exception as e:
        logger.error(f"Dataset cleaning pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")

@router.get("/download-clean/{session_id}")
async def download_clean_dataset(session_id: str):
    """Downloads the refined, model-ready, feature-engineered CSV."""
    pipeline = UniversalCleaningPipeline()
    try:
        csv_path = pipeline.get_clean_csv_path(session_id)
        return FileResponse(
            path=csv_path,
            filename=f"cleaned_model_ready_{session_id}.csv",
            media_type="text/csv"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Processed dataset session not found or expired.")

@router.get("/llm-status")
async def get_llm_status():
    """Checks local Ollama daemon connectivity and model availability."""
    llm_service = LLMService()
    status = await llm_service.check_ollama_status()
    return status
