import time

import pandas as pd
import pytest

from src.db.models import Loan
from src.pipelines.loading.loader import BatchLoader
from src.pipelines.loading.mapper import DataFrameMapper


@pytest.mark.performance
def test_batch_loading_throughput(db_session):
    """Generates 5,000 synthetic rows in-memory to benchmark SQLAlchemy bulk transaction constraints."""
    df = pd.DataFrame(
        {
            "id": [f"ID_{i}" for i in range(5000)],
            "annual_inc": [50000.0] * 5000,
        }
    )

    loader = BatchLoader(db_session, chunk_size=1000)
    models = DataFrameMapper.map_to_models(df, Loan)

    start = time.time()
    loader.load(models)
    duration = time.time() - start

    # SQLAlchemy bulk insertions over SQLite memory must strictly execute under 2 seconds.
    assert duration < 2.0
