import pandas as pd
import pytest

from src.pipelines.validation import ValidationPipeline
from src.pipelines.validation.business_validator import BusinessValidator, get_standard_loan_rules
from src.pipelines.validation.quality_validator import QualityValidator
from src.pipelines.validation.report import ValidationReport
from src.pipelines.validation.schema_validator import SchemaValidator


@pytest.fixture
def valid_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "loan_amnt": [1000.0, 5000.0, 10000.0],
            "int_rate": [5.5, 10.2, 15.0],
            "term": [36, 60, 36],
            "annual_inc": [50000, 60000, 120000],
        }
    )


@pytest.fixture
def invalid_df():
    return pd.DataFrame(
        {
            "id": [1, 1, 3],  # Duplicate PK
            "loan_amnt": [-500.0, 5000.0, 10000.0],  # Negative loan
            "int_rate": [5.5, 60.0, 15.0],  # High rate
            "annual_inc": [50000, -100, 120000],  # Negative income
        }
    )


def test_schema_validator_valid(valid_df):
    report = ValidationReport()
    validator = SchemaValidator(
        expected_schema={"id": "numeric", "loan_amnt": "numeric", "int_rate": "numeric"},
        required_columns=["id", "loan_amnt"],
        primary_keys=["id"],
    )
    validator.validate(valid_df, report)
    assert not report.fatal_errors
    assert any("term" in w for w in report.warnings) or any("annual_inc" in w for w in report.warnings)


def test_schema_validator_invalid(invalid_df):
    report = ValidationReport()
    validator = SchemaValidator(
        expected_schema={"id": "numeric"}, required_columns=["id", "missing_col"], primary_keys=["id"]
    )
    validator.validate(invalid_df, report)
    assert any("missing_col" in err for err in report.fatal_errors)


def test_business_rules_valid(valid_df):
    report = ValidationReport()
    validator = BusinessValidator(rules=get_standard_loan_rules())
    validator.validate(valid_df, report)
    assert not report.failed_checks


def test_business_rules_invalid(invalid_df):
    report = ValidationReport()
    validator = BusinessValidator(rules=get_standard_loan_rules())
    validator.validate(invalid_df, report)
    # loan_amnt <= 0, int_rate > 50, missing term, negative annual_inc
    assert len(report.business_rule_violations) > 0
    assert any("Positive Loan Amount" in err for err in report.business_rule_violations.keys())


def test_quality_validator(valid_df):
    report = ValidationReport()
    # Insert missing value for testing
    df = valid_df.copy()
    df.loc[0, "loan_amnt"] = None

    validator = QualityValidator(missing_threshold=0.2)
    validator.validate(df, report)

    assert report.dataset_statistics["num_rows"] == 3
    assert report.quality_metrics["missing_percentages"]["loan_amnt"] > 0
    assert "loan_amnt" in report.warnings[0] if report.warnings else False


def test_pipeline(valid_df):
    pipeline = ValidationPipeline(
        SchemaValidator({"id": "numeric"}, ["id"], ["id"]),
        BusinessValidator(get_standard_loan_rules()),
        QualityValidator(),
    )
    report = pipeline.run(valid_df)
    assert report.is_valid
    # Check that report is fully serializable
    assert isinstance(report.model_dump(), dict)
