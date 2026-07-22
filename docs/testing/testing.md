# Quality Engineering & Testing Strategy

The Fintech Analytics platform employs a rigorous Testing Pyramid enforcing safety, maintainability, and operational stability.

## 1. Test Pyramid
1. **Unit Tests (`tests/unit/`)**: Granular checks evaluating individual class behaviors (e.g., `test_features.py`, `test_analytics.py`).
2. **Integration Tests (`tests/integration/`)**: Evaluates cross-module workflows. For example, ensuring an uploaded CSV correctly navigates through Validation, Persistence, and surfaces accurately on the Analytics API.
3. **Smoke Tests (`tests/smoke/`)**: Lightweight dependency scans designed to quickly fail CI pipelines if databases or registries are incorrectly provisioned.
4. **Performance Tests (`tests/performance/`)**: Internal benchmarking guarding against memory leaks or transaction locks inside high-throughput loaders.

## 2. Fixtures
Database state is managed cleanly using Pytest `conftest.py` fixtures. It boots a lightweight `sqlite:///:memory:` instance, migrates schemas, and explicitly overrides FastAPI's `Depends(get_db)` hook statically. This guarantees zero side-effects.

## 3. Quality Tools & Execution
The platform rigidly enforces code quality through localized execution profiles:

### Pytest & Coverage
To execute tests and generate coverage matrices natively:
```bash
pytest --cov=src --cov-report=term --cov-report=xml --cov-report=html
```

### Static Analysis
Ruff operates as a high-speed rust-based linter, while MyPy ensures strict logical Type mappings:
```bash
ruff check src tests
mypy src tests
```
