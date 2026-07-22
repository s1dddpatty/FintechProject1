import shutil
import tempfile
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Body
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.api.schemas import IngestionSummary, DatasetAnalysisResponse, IngestionProcessRequest
from src.core.logging import get_logger
from src.db.models import Loan
from src.pipelines.ingestion.cleaner import DataCleaner
from src.pipelines.ingestion.normalizer import DataNormalizer
from src.pipelines.ingestion.reader import CSVReader, ParquetReader
from src.pipelines.ingestion.intelligence import DatasetIntelligenceEngine
from src.pipelines.loading.loader import BatchLoader
from src.pipelines.loading.mapper import DataFrameMapper
from src.pipelines.validation import (
    BusinessValidator,
    QualityValidator,
    SchemaValidator,
    ValidationPipeline,
    get_standard_loan_rules,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/ingestion", tags=["Data Pipeline"])

# Fallback backwards compatible endpoint (if UI still hits /upload directly)
@router.post("/upload", response_model=IngestionSummary)
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Redirect to analyze + process internally for backwards compatibility
    intelligence = DatasetIntelligenceEngine()
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
        
    analysis = intelligence.analyze(tmp_path, file.filename)
    return await process_dataset(
        request=IngestionProcessRequest(session_id=analysis["session_id"], mode="process_all"), 
        db=db
    )

@router.post("/analyze", response_model=DatasetAnalysisResponse)
async def analyze_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".parquet")):
        raise HTTPException(status_code=400, detail="Only CSV or Parquet files supported.")
        
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
        
    intelligence = DatasetIntelligenceEngine()
    analysis_result = intelligence.analyze(tmp_path, file.filename)
    
    return analysis_result


@router.post("/process", response_model=IngestionSummary)
async def process_dataset(request: IngestionProcessRequest, db: Session = Depends(get_db)):
    import time
    start_total = time.time()
    
    session_dir = Path("data/sessions")
    
    # Find the session file
    session_files = list(session_dir.glob(f"{request.session_id}.*"))
    if not session_files:
        raise HTTPException(status_code=404, detail="Session expired or not found.")
        
    session_file = session_files[0]
    is_csv = session_file.suffix == ".csv"

    try:
        reader = CSVReader() if is_csv else ParquetReader()
        
        # Parse the mode for sampling
        sample_size = None
        mode_instruction = request.mode
        
        if mode_instruction.startswith("sample_"):
            size_str = mode_instruction.split("_")[1]
            if size_str.endswith("k"):
                sample_size = int(size_str.replace("k", "")) * 1000
            else:
                sample_size = int(size_str)
                
        # Read dataset safely
        if is_csv:
            df = reader.read(session_file, mode=mode_instruction, sample_size=sample_size)
        else:
            df = reader.read(session_file) # Parquet not yet supported for smart sampling

        total_rows = len(df)

        cleaner = DataCleaner()
        df = cleaner.clean(df)

        normalizer = DataNormalizer(bool_columns=[], currency_columns=[])
        df = normalizer.normalize(df)

        # Validation Timing
        start_val = time.time()
        schema_validator = SchemaValidator(
            expected_schema={
                "id": "numeric",
                "loan_amnt": "numeric",
                "int_rate": "numeric",
            },
            required_columns=["id", "loan_amnt"],
            primary_keys=[]
        )
        business_validator = BusinessValidator(rules=get_standard_loan_rules())
        quality_validator = QualityValidator()

        validator = ValidationPipeline(
            schema_validator=schema_validator,
            business_validator=business_validator,
            quality_validator=quality_validator
        )
        report = validator.run(df)
        val_time = time.time() - start_val

        if report.fatal_errors:
            error_detail = {"fatal_errors": report.fatal_errors, "warnings": report.warnings}
            logger.error(f"Validation failed with fatal errors: {error_detail}")
            raise HTTPException(status_code=400, detail=error_detail)

        # Apply soft validation (keep only valid rows)
        if hasattr(report, "valid_indices") and report.valid_indices is not None:
            if len(report.valid_indices) == 0:
                error_detail = "Zero valid records remaining after validation."
                logger.error(f"Validation soft filtering failed: {error_detail}. Original rows: {total_rows}")
                raise HTTPException(status_code=400, detail=error_detail)
            df = df.iloc[report.valid_indices]

        accepted_rows = len(df)
        rejected = total_rows - accepted_rows
        success_rate = (accepted_rows / total_rows) * 100 if total_rows > 0 else 0.0

        # DB Insertion Timing
        start_db = time.time()
        loader = BatchLoader(db)
        
        # Insert loans (which now includes the Applicant Snapshot)
        loan_models = DataFrameMapper.map_to_models(df, Loan)
        loader.load(loan_models)
        db_time = time.time() - start_db

        return IngestionSummary(
            rows_processed=total_rows,
            rows_accepted=accepted_rows,
            rows_rejected=rejected,
            success_rate=round(success_rate, 2),
            validation_status="Passed with Warnings" if rejected > 0 else "Passed",
            validation_warnings=report.warnings,
            business_rule_violations=getattr(report, "business_rule_violations", {}),
            sample_rejected_indices=getattr(report, "invalid_indices", [])[:10],
            ingestion_time=time.time() - start_total,
            validation_time=val_time,
            db_insertion_time=db_time
        )
    finally:
        # Cleanup the session file
        if session_file.exists():
            session_file.unlink()
