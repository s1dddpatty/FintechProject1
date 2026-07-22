from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "database" in data
    assert "version" in data


def test_get_models():
    response = client.get("/models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_missing_route():
    response = client.get("/missing")
    assert response.status_code == 404
