from pathlib import Path

import pytest

from tests.fixtures.sample_data import create_sample_csv


@pytest.mark.integration
def test_ingestion_and_analytics_pipeline(client):
    csv_path = create_sample_csv()

    # Test Full CSV Ingestion flow via API
    with open(csv_path, "rb") as f:
        response = client.post("/ingestion/upload", files={"file": ("sample.csv", f, "text/csv")})

    assert response.status_code == 200
    data = response.json()
    assert data["rows_processed"] == 3
    assert data["validation_status"] == "Passed"

    # Verify the database has the persisted data via the Analytics engine
    portfolio_resp = client.get("/analytics/portfolio")
    assert portfolio_resp.status_code == 200

    portfolio_data = portfolio_resp.json()
    assert portfolio_data["total_loans"]["value"] == 3
    assert portfolio_data["total_funded"]["value"] == 30000.0

    Path(csv_path).unlink()
