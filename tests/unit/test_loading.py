from unittest.mock import Mock

import pandas as pd
import pytest
from sqlalchemy.exc import IntegrityError

from src.db.models import Loan
from src.pipelines.loading.exceptions import BatchInsertError
from src.pipelines.loading.loader import BatchLoader
from src.pipelines.loading.mapper import DataFrameMapper


def test_mapper():
    df = pd.DataFrame({"id": ["A1", "B2"], "annual_inc": [50000.0, 100000.0]})

    models = DataFrameMapper.map_to_models(df, Loan)

    assert len(models) == 2
    assert isinstance(models[0], Loan)
    assert models[0].id == "A1"
    assert models[0].annual_inc == 50000.0


def test_loader_success():
    mock_session = Mock()
    loader = BatchLoader(session=mock_session, chunk_size=2)

    models = [Loan(id=f"ID_{i}") for i in range(5)]
    loader.load(models)

    # 5 models, chunk size 2 -> 3 chunks (2, 2, 1) -> 3 execute calls
    assert mock_session.execute.call_count == 3
    assert mock_session.flush.call_count == 3
    # 1 final commit
    mock_session.commit.assert_called_once()


def test_loader_rollback():
    mock_session = Mock()
    # Force flush to raise a SQLAlchemy exception mimicking a Unique Constraint Violation
    mock_session.flush.side_effect = IntegrityError(None, None, Exception("Unique constraint failed"))

    loader = BatchLoader(session=mock_session)
    models = [Loan(id="A1")]

    with pytest.raises(BatchInsertError):
        loader.load(models)

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
