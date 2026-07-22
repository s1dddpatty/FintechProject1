from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from src.pipelines.ingestion.cleaner import DataCleaner
from src.pipelines.ingestion.exceptions import DataReaderError
from src.pipelines.ingestion.normalizer import DataNormalizer
from src.pipelines.ingestion.pipeline import IngestionPipeline
from src.pipelines.ingestion.reader import CSVReader


@pytest.fixture
def dirty_df():
    return pd.DataFrame(
        {
            " Loan Amnt ": [" $1,000.00 ", "5000", "", np.nan],
            "issue_d": ["2023-01-01", "02/01/2023", "bad_date", None],
            "is_default": ["Yes", "NO", "t", "False"],
            "State": [" CA ", "NY", "N/A", "TX"],
        }
    )


def test_csv_reader_error():
    reader = CSVReader()
    with pytest.raises(DataReaderError):
        reader.read("non_existent_file.csv")


def test_data_cleaner(dirty_df):
    cleaner = DataCleaner()
    # add an empty row and a duplicate row
    df = pd.concat(
        [dirty_df, pd.DataFrame([[np.nan] * 4], columns=dirty_df.columns), dirty_df.iloc[[0]]], ignore_index=True
    )

    cleaned = cleaner.clean(df)

    # Empty row and duplicate dropped
    assert len(cleaned) == 4

    # Whitespace trimmed
    assert cleaned.iloc[0]["State"] == "CA"

    # Nulls normalized
    assert pd.isna(cleaned.iloc[2][" Loan Amnt "])  # empty string -> nan
    assert pd.isna(cleaned.iloc[2]["State"])  # N/A -> nan


def test_data_normalizer(dirty_df):
    normalizer = DataNormalizer(
        date_columns=["issue_d"],
        bool_columns=["is_default"],
        currency_columns=["loan_amnt"],  # column names will be normalized first
    )

    normalized = normalizer.normalize(dirty_df)

    # Column name normalized
    assert "loan_amnt" in normalized.columns
    assert "state" in normalized.columns

    # Currencies normalized
    assert normalized.iloc[0]["loan_amnt"] == 1000.0

    # Dates normalized
    assert pd.api.types.is_datetime64_any_dtype(normalized["issue_d"])

    # Booleans normalized
    assert normalized.iloc[0]["is_default"] is True
    assert normalized.iloc[1]["is_default"] is False
    assert normalized.iloc[2]["is_default"] is True
    assert normalized.iloc[3]["is_default"] is False


def test_ingestion_pipeline():
    mock_reader = Mock()
    mock_reader.read.return_value = pd.DataFrame({"id": [1]})

    mock_validator = Mock()
    mock_report = Mock()
    mock_report.is_valid = True
    mock_report.failed_checks = []
    mock_validator.run.return_value = mock_report

    pipeline = IngestionPipeline(
        reader=mock_reader, cleaner=DataCleaner(), normalizer=DataNormalizer(), validator=mock_validator
    )

    df, report = pipeline.run("dummy.csv")

    assert len(df) == 1
    assert report.is_valid
    mock_reader.read.assert_called_once_with("dummy.csv")
    mock_validator.run.assert_called_once()
