# Fintech Analytics Platform

An enterprise-grade, production-ready Machine Learning and Data Engineering orchestration platform for lending portfolio analytics.

Built entirely decoupled across Clean Architecture boundaries, this repository handles data ingestion, rigorous schema validation, feature engineering pipelines, model training, prediction registries, and business analytics seamlessly via a FastAPI gateway.

---

## Highlights

- **Production-style Clean Architecture**
- **SQLAlchemy 2.x Repository Pattern**
- **Feature Engineering Pipeline**
- **Model Registry**
- **REST API with FastAPI**
- **Dockerized deployment**
- **GitHub Actions CI**
- **Prometheus metrics**
- **Structured JSON logging**
- **Enterprise testing strategy**
- **Dependency Injection**
- **Type-safe Pydantic models**

---

## Architecture Diagrams

### 1. System Architecture

```text
Browser / Dashboard
        │
        ▼
     FastAPI
        │
 ┌──────┼─────────┐
 ▼      ▼         ▼
Analytics  Prediction  Ingestion
        │
        ▼
Feature Engineering
        │
        ▼
   ML Platform
        │
        ▼
   PostgreSQL
```

### 2. Data Flow

```text
       CSV
        │
        ▼
      Reader
        │
        ▼
     Cleaner
        │
        ▼
    Normalizer
        │
        ▼
    Validation
        │
        ▼
   Persistence
        │
        ▼
    Analytics
        │
        ▼
Feature Engineering
        │
        ▼
       ML
```

### 3. Request Flow

```text
    Browser
        │
        ▼
    REST API
        │
        ▼
    Service
        │
        ▼
   Repository
        │
        ▼
    Database
```

---

## Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **API Framework** | FastAPI, Uvicorn, Pydantic |
| **Data Engineering** | Pandas, Numpy, PyArrow |
| **Machine Learning** | Scikit-Learn |
| **Database & ORM** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **Quality & Testing** | Pytest, Ruff, Mypy, Coverage, Pip-Audit |
| **Observability** | Prometheus-Client, ContextVars, Logging |
| **Infrastructure** | Docker, GitHub Actions |

---

## Quick Start

### Docker (Production-Ready)
To spin up the entire isolated stack including PostgreSQL and the API:

```bash
docker-compose up --build -d
```

Access the API dynamically at `http://localhost:8000/docs`

### Local Development (Recommended)

Run the PostgreSQL database inside Docker while running the FastAPI backend and Next.js frontend natively for instant hot-reloading and easy debugging.

```bash
# 1. Start PostgreSQL in Docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db

# 2. Run Database Migrations (Native)
python -m venv .venv
# On Windows: .\.venv\Scripts\activate
# On Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 3. Boot FastAPI Backend (Native)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Boot Next.js Frontend (Native)
cd frontend
npm install
npm run dev
```

---

## API Overview & Examples

### Health Probes
```bash
# Check application liveness
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics
```

### 1. Ingestion Endpoint
Ingests a CSV dataset, cleans it, validates it, and persists the ORM objects.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
     -H "Content-Type: application/json" \
     -d '{"source_path": "data/raw/lending_data.csv"}'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "records_ingested": 10500,
  "validation_report": {
    "is_valid": true,
    "failed_checks": []
  }
}
```

### 2. Prediction Endpoint
Calculates lending risk probabilities via a serialized algorithm loaded directly from the `ModelRegistry`.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "model_id": "risk_model_v1",
           "customer_data": {
               "annual_income": 75000,
               "loan_amount": 15000,
               "employment_length": 5
           }
         }'
```

**Response (200 OK):**
```json
{
  "prediction": "APPROVED",
  "probability": 0.82,
  "model_version": "v1.0.0"
}
```

**Error Example (400 Bad Request):**
```json
{
  "error_code": "PredictionError",
  "message": "Prediction dataset missing required features: ['debt_to_income']",
  "timestamp": 1721590000.0
}
```

---

## Machine Learning Overview

The ML core (`src/ml` and `src/features`) abstracts algorithm integration entirely away from application endpoints. 
- **Feature Engineering**: Decoupled `Transformers`, `Scalers`, and `Encoders`.
- **Model Registry**: Persists metadata JSON and Pickled models across restarts dynamically mapping semantic IDs (e.g. `random_forest_v1`).
- **Prediction Pipeline**: Infers exact feature columns required by the exact requested model ID organically mitigating train-serving skews.

---

## Repository Structure

```text
├── .github/workflows/   # CI/CD pipelines
├── docs/                # Architectural Decision Records (ADR)
├── src/                 
│   ├── analytics/       # Business intelligence calculations
│   ├── api/             # FastAPI routers, middleware, and dependency injection
│   ├── core/            # Configuration and global exceptions
│   ├── db/              # SQLAlchemy models and Repository pattern logic
│   ├── features/        # Feature Engineering 
│   ├── ml/              # Model training, registry, evaluation
│   ├── observability/   # Prometheus metrics, unstructured logging tracing
│   └── pipelines/       # Ingestion and Validation DAGs
├── tests/               # Pytest suite
├── docker-compose.yml   # Multi-container orchestration
├── Dockerfile           # Distroless application packaging
├── requirements.txt     # Locked production dependencies
└── pytest.ini           # Testing configurations
```

---

## Screenshots

*(Placeholder: UI/Dashboard and OpenAPI visual demonstrations will be mapped here)*

---

## Contributing
Refer to [CONTRIBUTING.md](CONTRIBUTING.md) for pull request formats and our `Clean Architecture` boundaries. Please review our [CODE OF CONDUCT](CODE_OF_CONDUCT.md).

---

## License
Distributed under the [Apache License 2.0](LICENSE).

---

## Skills Demonstrated

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Pandas**
- **Scikit-Learn**
- **Machine Learning**
- **Feature Engineering**
- **Docker**
- **GitHub Actions**
- **Prometheus**
- **REST APIs**
- **Clean Architecture**
- **Repository Pattern**
- **Dependency Injection**
- **CI/CD**
- **Testing**
- **Observability**
- **Data Engineering**
- **MLOps Fundamentals**
