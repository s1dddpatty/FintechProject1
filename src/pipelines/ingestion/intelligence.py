import os
import uuid
import time
import chardet
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger(__name__)

class DatasetIntelligenceEngine:
    """Analyzes datasets safely without loading them entirely into memory."""

    def __init__(self):
        self.session_dir = Path("data/sessions")
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, file_path: Path, original_filename: str) -> Dict[str, Any]:
        """Performs a lightweight analysis of the file and moves it to a session."""
        start_time = time.time()
        logger.info(f"Analyzing uploaded file: {original_filename}")
        
        file_size_bytes = os.path.getsize(file_path)
        
        # 1. Determine encoding and delimiter
        with open(file_path, "rb") as f:
            raw_preview = f.read(10000)
            
        encoding_result = chardet.detect(raw_preview)
        encoding = encoding_result['encoding'] or 'utf-8'
        
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            header_line = f.readline()
            delimiter = "," if "," in header_line else "\t" if "\t" in header_line else ";"
            headers = [h.strip().strip('"') for h in header_line.split(delimiter)]
            column_count = len(headers)
            
            # Count rows efficiently
            row_count = 0
            for _ in f:
                row_count += 1
                
        # 2. Schema Checks
        required_features = ["id", "loan_amnt"]
        target_column = settings.model_target_column
        
        missing_required = [req for req in required_features if req not in headers]
        required_avail = len(missing_required) == 0
        target_avail = target_column in headers
        
        # 3. Categorize & Memory
        estimated_ram_mb = (file_size_bytes * 8) / (1024 * 1024)
        
        if row_count > settings.max_safe_rows:
            category = "LARGE"
            recommendation = "Stratified Sample" if target_avail else "Random Sample"
        elif row_count > settings.medium_dataset_threshold:
            category = "MEDIUM"
            recommendation = "Stratified Sample" if target_avail else "Random Sample"
        else:
            category = "SMALL"
            recommendation = "None"
            
        strategy = "stratified" if target_avail else "random"
            
        # 4. Lightweight Pandas Profile (First 100 rows only)
        try:
            df_preview = pd.read_csv(file_path, nrows=100, sep=delimiter, encoding=encoding)
            numeric_cols = sum(1 for dtype in df_preview.dtypes if pd.api.types.is_numeric_dtype(dtype))
            datetime_cols = sum(1 for dtype in df_preview.dtypes if pd.api.types.is_datetime64_any_dtype(dtype))
            bool_cols = sum(1 for dtype in df_preview.dtypes if pd.api.types.is_bool_dtype(dtype))
            categorical_cols = column_count - numeric_cols - datetime_cols - bool_cols
            target_type = str(df_preview[target_column].dtype) if target_avail else "Unknown"
        except Exception as e:
            logger.warning(f"Could not generate dataset profile: {e}")
            numeric_cols = 0
            datetime_cols = 0
            bool_cols = 0
            categorical_cols = 0
            target_type = "Unknown"
            
        # 5. Future Extensibility Hook
        self._run_future_checks(file_path)
            
        # 6. Session Management
        session_id = str(uuid.uuid4())
        session_file = self.session_dir / f"{session_id}{Path(original_filename).suffix}"
        
        import shutil
        shutil.move(str(file_path), str(session_file))
        
        duration = time.time() - start_time
        
        # Construct Health Report
        return {
            "session_id": session_id,
            "filename": original_filename,
            "dataset_category": category,
            "estimated_ram_mb": round(estimated_ram_mb, 2),
            "general": {
                "row_count": row_count,
                "column_count": column_count,
                "file_size_bytes": file_size_bytes,
                "delimiter": delimiter,
                "encoding": encoding
            },
            "schema_info": {
                "required_columns_present": required_avail,
                "missing_required_columns": missing_required,
                "target_column": target_column,
                "target_column_found": target_avail
            },
            "profile": {
                "numeric_columns": numeric_cols,
                "categorical_columns": categorical_cols,
                "datetime_columns": datetime_cols,
                "boolean_columns": bool_cols,
                "target_column_type": target_type
            },
            "sampling": {
                "strategy": strategy,
                "recommendation": recommendation
            },
            "config_snapshot": {
                "configured_target_column": target_column,
                "dataset_mode": settings.dataset_mode,
                "medium_threshold": settings.medium_dataset_threshold,
                "max_safe_rows": settings.max_safe_rows,
                "default_sample_size": settings.default_sample_size
            },
            "metadata": {
                "dataset_version": "Unknown",
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                "analysis_duration_sec": round(duration, 4)
            }
        }
        
    def _run_future_checks(self, file_path: Path):
        """
        Stub for future extensibility.
        Can be expanded to run lightweight checks for:
        - Missing value percentages
        - Duplicate row detection
        - Constant columns
        - High-cardinality categoricals
        """
        pass
