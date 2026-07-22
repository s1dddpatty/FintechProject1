"""
Data Validation Engine.
Provides schema, business logic, and data quality validation.
"""

from .business_validator import BusinessRule, BusinessValidator, get_standard_loan_rules
from .exceptions import BusinessRuleValidationError, SchemaValidationError, ValidationError
from .quality_validator import QualityValidator
from .report import ValidationReport
from .schema_validator import SchemaValidator


class ValidationPipeline:
    """Orchestrates the validation execution."""

    def __init__(
        self,
        schema_validator: SchemaValidator,
        business_validator: BusinessValidator,
        quality_validator: QualityValidator,
    ):
        self.schema_validator = schema_validator
        self.business_validator = business_validator
        self.quality_validator = quality_validator

    def run(self, df) -> ValidationReport:
        import logging
        log = logging.getLogger(__name__)
        report = ValidationReport()
        # Initialize valid_indices to all rows by default
        report.valid_indices = list(range(len(df)))
        
        log.info(f"--- ValidationPipeline Start ---")
        log.info(f"Rows entering schema validation: {len(df)}")
        self.schema_validator.validate(df, report)
        log.info(f"Rows leaving schema validation: {len(df)}")
        log.info(f"Schema fatal errors: {report.fatal_errors}")
        log.info(f"Schema failed checks: {report.failed_checks}")
        log.info(f"Schema warnings: {report.warnings}")

        # Skip business/quality checks if schema is fundamentally broken with fatal errors
        # Changed from report.failed_checks to report.fatal_errors because type mismatches shouldn't necessarily skip business checks if we can proceed, or at least we should log why it was skipped.
        if not report.fatal_errors:
            log.info(f"Rows entering business validation: {len(df)}")
            self.business_validator.validate(df, report)
            log.info(f"Rows leaving business validation: {len(df)}")
            log.info(f"Valid indices: {len(report.valid_indices)}, Invalid indices: {len(report.invalid_indices)}")
            
            log.info(f"Rows entering quality validation: {len(df)}")
            self.quality_validator.validate(df, report)
            log.info(f"Rows leaving quality validation: {len(df)}")
        else:
            log.info("Skipping business and quality validation due to fatal schema errors.")

        log.info(f"--- ValidationPipeline End ---")

        report.finalize()
        return report


__all__ = [
    "ValidationReport",
    "SchemaValidator",
    "BusinessValidator",
    "BusinessRule",
    "get_standard_loan_rules",
    "QualityValidator",
    "ValidationPipeline",
    "ValidationError",
    "SchemaValidationError",
    "BusinessRuleValidationError",
]
