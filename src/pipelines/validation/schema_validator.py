"""
Schema validation engine.
"""

from typing import Dict, List

import pandas as pd

from src.core.logging import get_logger
from src.pipelines.validation.report import ValidationReport

logger = get_logger(__name__)


class SchemaValidator:
    """Validates dataframe schema against expected definitions."""

    def __init__(self, expected_schema: Dict[str, str], required_columns: List[str], primary_keys: List[str]):
        self.expected_schema = expected_schema
        self.required_columns = required_columns
        self.primary_keys = primary_keys

    def validate(self, df: pd.DataFrame, report: ValidationReport) -> None:
        logger.info("Starting schema validation...")
        self._check_required_columns(df, report)
        if report.fatal_errors:
            logger.error("Schema validation failed on required columns. Skipping further schema checks.")
            return

        self._check_unexpected_columns(df, report)
        self._check_data_types(df, report)
        self._check_primary_key_uniqueness(df, report)
        logger.info("Schema validation complete.")

    def _check_required_columns(self, df: pd.DataFrame, report: ValidationReport) -> None:
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            report.add_fatal("Required Columns", f"Missing columns: {missing}")
        else:
            report.add_passed("Required Columns")

    def _check_unexpected_columns(self, df: pd.DataFrame, report: ValidationReport) -> None:
        unexpected = [col for col in df.columns if col not in self.expected_schema]
        if unexpected:
            report.add_warning(f"Unexpected columns found: {unexpected}")
        else:
            report.add_passed("Unexpected Columns")

    def _check_data_types(self, df: pd.DataFrame, report: ValidationReport) -> None:
        type_failures = []
        for col, expected_type in self.expected_schema.items():
            if col in df.columns:
                actual_dtype = str(df[col].dtype)
                if expected_type == "numeric" and not pd.api.types.is_numeric_dtype(df[col]):
                    type_failures.append(f"{col} expected numeric but got {actual_dtype}")
                elif (
                    expected_type == "string"
                    and not pd.api.types.is_string_dtype(df[col])
                    and not pd.api.types.is_object_dtype(df[col])
                ):
                    type_failures.append(f"{col} expected string but got {actual_dtype}")

        if type_failures:
            report.add_failed("Data Types", "; ".join(type_failures))
        else:
            report.add_passed("Data Types")

    def _check_primary_key_uniqueness(self, df: pd.DataFrame, report: ValidationReport) -> None:
        for pk in self.primary_keys:
            if pk in df.columns:
                duplicates = int(df[pk].duplicated().sum())
                if duplicates > 0:
                    report.add_failed("Primary Key Uniqueness", f"Column '{pk}' has {duplicates} duplicate values.")
                else:
                    report.add_passed(f"Primary Key Uniqueness ({pk})")
