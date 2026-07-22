"""
Ingestion Pipeline Orchestrator.
"""

from typing import Any, Tuple

import pandas as pd

from src.core.logging import get_logger
from src.observability.metrics import track_ingestion
from src.pipelines.validation import ValidationPipeline, ValidationReport

from .cleaner import DataCleaner
from .normalizer import DataNormalizer
from .reader import BaseReader

logger = get_logger(__name__)


class IngestionPipeline:
    """
    Orchestrates reading, cleaning, normalizing, and validating datasets.
    """

    def __init__(
        self, reader: BaseReader, cleaner: DataCleaner, normalizer: DataNormalizer, validator: ValidationPipeline
    ):
        self.reader = reader
        self.cleaner = cleaner
        self.normalizer = normalizer
        self.validator = validator

    @track_ingestion
    def run(self, source: Any) -> Tuple[pd.DataFrame, ValidationReport]:
        logger.info(f"Starting ingestion pipeline for source: {source}")

        # 1. Read
        raw_df = self.reader.read(source)

        # 2. Clean
        cleaned_df = self.cleaner.clean(raw_df)

        # 3. Normalize
        normalized_df = self.normalizer.normalize(cleaned_df)

        # 4. Validate
        report = self.validator.run(normalized_df)

        if report.is_valid:
            logger.info("Ingestion and validation pipeline completed successfully.")
        else:
            logger.warning(
                f"Ingestion pipeline completed with validation errors: {len(report.failed_checks)} failures."
            )

        return normalized_df, report
