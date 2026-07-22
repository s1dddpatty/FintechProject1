import pytest


@pytest.mark.smoke
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["database"] == "ok"
    assert data["registry"] == "ok"
    assert "version" in data
