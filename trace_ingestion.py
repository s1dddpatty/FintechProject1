from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

with open("benchmarks/dataset_100.csv", "rb") as f:
    response = client.post("/ingestion/upload", files={"file": f})

print(response.status_code)
print(response.json())
