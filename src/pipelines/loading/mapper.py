from typing import List, Type

import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.db.base import Base

from .exceptions import DataMappingError

logger = get_logger(__name__)


class DataFrameMapper:
    """Converts Pandas DataFrames to SQLAlchemy ORM models."""

    @staticmethod
    def map_to_models(df: pd.DataFrame, model_class: Type[Base]) -> List[Base]:
        logger.info(f"Mapping {len(df)} rows to {model_class.__name__} models...")
        try:
            # Replace NaNs with None for SQL insertion to prevent Postgres rejecting float NaNs
            clean_df = df.replace({np.nan: None})
            records = clean_df.to_dict(orient="records")
            
            # Filter kwargs to only match the target model's column names
            valid_keys = [c.name for c in model_class.__table__.columns]
            
            models = []
            for record in records:
                filtered_record = {k: v for k, v in record.items() if k in valid_keys}
                models.append(model_class(**filtered_record))
                
            logger.info("Mapping successful.")
            return models
        except Exception as e:
            logger.error(f"Failed to map DataFrame to models: {e}")
            raise DataMappingError(f"Mapping failed: {e}")
