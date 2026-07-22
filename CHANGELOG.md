# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - Initial Open-Source Release

### Added
- **Core Architecture**: Clean Architecture setup with decoupled Domain, Application, and Infrastructure layers.
- **Data Ingestion Pipeline**: Modular `Reader`, `Cleaner`, and `Normalizer` interfaces supporting CSV/Parquet.
- **Validation Engine**: Pydantic schema validation and business rule validation pipeline.
- **Persistence Layer**: SQLAlchemy Repository Pattern (`CustomerRepository`, `LoanRepository`, `PaymentRepository`, `PredictionRepository`).
- **Feature Engineering Platform**: Scikit-learn compatible derived transformers, categorical encoders, and scalers.
- **Machine Learning Platform**: Dynamic `ModelRegistry`, `ModelTrainer` supporting standard algorithms (Logistic Regression, Random Forest, Gradient Boosting), and `ModelEvaluator`.
- **Analytics Engine**: Centralized computational classes for `Risk`, `Portfolio`, `Customer`, `Loan`, and `Executive` analytics.
- **API Gateway**: Production-ready FastAPI service orchestrating the pipelines safely.
- **Observability**: Prometheus metrics, structured JSON logging, tracing contexts (correlation IDs), and robust health probes (`/live`, `/ready`, `/health`).
- **Quality Assurance**: Complete GitHub Actions CI pipeline running Ruff, MyPy, Pytest, and Pip-Audit natively.
- **Docker**: Optimized multi-stage Dockerfile mimicking a distroless production runtime.

### Changed
- Refactored all implicit `Optional` arguments to strictly comply with `PEP 484` and `mypy` strict definitions.
- Resolved conflicting linters to standardize purely on `ruff`.

### Removed
- Unused testing artifacts and overlapping legacy exceptions.
