"""
Data quality and statistics validation engine.
"""

import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.pipelines.validation.report import ValidationReport

logger = get_logger(__name__)


class QualityValidator:
    """Calculates quality metrics, missing value rates, and statistical summaries."""

    def __init__(self, missing_threshold: float = 0.5):
        self.missing_threshold = missing_threshold

    def validate(self, df: pd.DataFrame, report: ValidationReport) -> None:
        logger.info("Starting data quality validation...")

        # Row / Col Counts
        report.dataset_statistics["num_rows"] = len(df)
        report.dataset_statistics["num_columns"] = len(df.columns)

        # Missing values
        missing_counts = df.isnull().sum()
        missing_pct = missing_counts / len(df)
        high_missing_cols = missing_pct[missing_pct > self.missing_threshold].index.tolist()

        if high_missing_cols:
            report.add_warning(f"Columns exceeding missing threshold ({self.missing_threshold}): {high_missing_cols}")

        report.quality_metrics["missing_percentages"] = missing_pct.to_dict()

        # Duplicates
        duplicate_pct = float(df.duplicated().sum() / len(df)) if len(df) > 0 else 0.0
        report.quality_metrics["duplicate_percentage"] = duplicate_pct
        if duplicate_pct > 0.05:
            report.add_warning(f"High global duplicate rate: {duplicate_pct:.1%}")

        # Basic Stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = {}
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()

            stats[col] = {
                "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                "outliers_count": int(outliers),
            }

        report.quality_metrics["numeric_statistics"] = stats
        report.add_passed("Data Quality Assessment")
        logger.info("Data quality validation complete.")
