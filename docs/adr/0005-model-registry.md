# ADR 0005: Model Registry

## Status
Accepted

## Context
Predictors need to query models dynamically without recompiling the application. Hardcoding pickled models into the API breaks scalability and makes AB testing impossible.

## Decision
We implemented a local file-based `ModelRegistry` mapping unique string IDs to their underlying `.pkl` serialized artifacts and corresponding JSON `metadata` schema.

## Consequences
- **Positive**: FastAPI can blindly query `Predictor.predict(model_id="v2")` without caring what algorithm "v2" uses internally.
- **Negative**: The current file-system implementation prevents horizontal multi-node scaling without a shared network volume. We will migrate to a cloud-storage registry (e.g., S3/GCS) in the future.
