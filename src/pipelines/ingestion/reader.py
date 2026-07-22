"""
Data readers for the ingestion pipeline.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd

from src.core.logging import get_logger

from .exceptions import DataReaderError
from src.core.config import settings

logger = get_logger(__name__)


class BaseReader(ABC):
    """Abstract interface for all data readers."""

    @abstractmethod
    def read(self, source: Any) -> pd.DataFrame:
        pass


class CSVReader(BaseReader):
    """Reads data from a CSV file."""

    def read(self, source: str | Path, mode: str = "process_all", sample_size: int = None) -> pd.DataFrame:
        logger.info(f"Reading CSV from source: {source} with mode: {mode}")
        try:
            if mode == "process_all":
                return pd.read_csv(source)
                
            if not sample_size:
                raise DataReaderError("sample_size must be provided when sampling.")
                
            # Perform memory-efficient sampling
            logger.info(f"Performing memory-efficient stratified sampling for {sample_size} rows...")
            
            # 1. Read only the target column to find distribution
            try:
                target_df = pd.read_csv(source, usecols=[settings.model_target_column])
                has_target = True
            except ValueError:
                # Target column not found, fallback to random sampling
                has_target = False
                logger.warning(f"Target column '{settings.model_target_column}' not found. Falling back to random sampling.")
                
            import numpy as np
            
            if has_target:
                from sklearn.model_selection import StratifiedShuffleSplit
                
                # If dataset is smaller than sample size, just read all
                if len(target_df) <= sample_size:
                    return pd.read_csv(source)
                    
                sss = StratifiedShuffleSplit(n_splits=1, train_size=sample_size, random_state=42)
                
                # Generate indices to keep
                try:
                    indices_to_keep, _ = next(sss.split(np.zeros(len(target_df)), target_df[settings.model_target_column].fillna("Missing")))
                except ValueError as e:
                    logger.warning(f"Stratified sampling failed ({e}). Falling back to random sampling.")
                    indices_to_keep = np.random.choice(len(target_df), sample_size, replace=False)
            else:
                # Need row count for random sampling without target column
                with open(source, "r", encoding="utf-8", errors="ignore") as f:
                    row_count = sum(1 for _ in f) - 1 # excluding header
                    
                if row_count <= sample_size:
                    return pd.read_csv(source)
                    
                indices_to_keep = np.random.choice(row_count, sample_size, replace=False)
                
            # Convert to 1-indexed set for skiprows (0 is header)
            indices_set = set(indices_to_keep + 1)
            
            # 2. Read only the selected rows into memory
            # skiprows takes a callable that returns True if the row should be skipped
            return pd.read_csv(source, skiprows=lambda i: i > 0 and i not in indices_set)
            
        except Exception as e:
            logger.error(f"Failed to read CSV from {source}: {e}")
            raise DataReaderError(f"CSV read failed: {e}")


class ParquetReader(BaseReader):
    """Reads data from a Parquet file."""

    def read(self, source: str | Path) -> pd.DataFrame:
        logger.info(f"Reading Parquet from source: {source}")
        try:
            return pd.read_parquet(source)
        except Exception as e:
            logger.error(f"Failed to read Parquet from {source}: {e}")
            raise DataReaderError(f"Parquet read failed: {e}")
