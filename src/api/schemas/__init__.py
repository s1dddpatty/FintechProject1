from typing import Any, Dict, List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str
    registry: str
    version: str
    timestamp: float


class PredictionRequest(BaseModel):
    features: List[Dict[str, Any]]


class PredictionResponse(BaseModel):
    prediction: List[int]
    probability: List[float]
    model_identifier: str
    timestamp: float


class IngestionSummary(BaseModel):
    rows_processed: int
    rows_accepted: int
    rows_rejected: int
    success_rate: float
    validation_status: str
    validation_warnings: List[str] = []
    business_rule_violations: Dict[str, str] = {}
    sample_rejected_indices: List[int] = []
    ingestion_time: float = 0.0
    validation_time: float = 0.0
    db_insertion_time: float = 0.0

class DatasetGeneral(BaseModel):
    row_count: int
    column_count: int
    file_size_bytes: int
    delimiter: str
    encoding: str

class DatasetSchema(BaseModel):
    required_columns_present: bool
    missing_required_columns: List[str]
    target_column: str
    target_column_found: bool

class DatasetProfile(BaseModel):
    numeric_columns: int
    categorical_columns: int
    datetime_columns: int
    boolean_columns: int
    target_column_type: str

class DatasetSampling(BaseModel):
    strategy: str
    recommendation: str

class DatasetConfigSnapshot(BaseModel):
    configured_target_column: str
    dataset_mode: str
    medium_threshold: int
    max_safe_rows: int
    default_sample_size: int

class DatasetMetadata(BaseModel):
    dataset_version: str
    analysis_timestamp: str
    analysis_duration_sec: float

class DatasetAnalysisResponse(BaseModel):
    session_id: str
    filename: str
    dataset_category: str
    estimated_ram_mb: float
    general: DatasetGeneral
    schema_info: DatasetSchema
    profile: DatasetProfile
    sampling: DatasetSampling
    config_snapshot: DatasetConfigSnapshot
    metadata: DatasetMetadata

class IngestionProcessRequest(BaseModel):
    session_id: str
    mode: str # "process_all", "sample_250k", "sample_500k", etc.


class ResetDatasetRequest(BaseModel):
    keep_models: bool = True
    dry_run: bool = False

class ResetDatasetResponse(BaseModel):
    loans_deleted: int
    predictions_deleted: int
    payments_deleted: int
    models_deleted: bool
    database_ready: bool
    message: str
