# ADR 0007: Why FastAPI Was Chosen

## Status
Accepted

## Context
We needed to select a primary Web API framework to act as the REST orchestration layer over our Data Engineering and ML pipelines.

## Decision
We selected **FastAPI**.

### FastAPI vs. Flask
Flask is historically common but relies on older synchronous WSGI patterns and third-party extensions for OpenAPI (Swagger) generation. FastAPI leverages native Python type hints to generate OpenAPI schemas automatically, while validating input inherently using Pydantic.

### FastAPI vs. Django
Django is tightly coupled to its "Batteries Included" ORM and architecture. Implementing Clean Architecture (Domain Driven Design) alongside Django often involves overriding the framework entirely, fighting its native monolithic constraints.

### Why it fits this architecture
FastAPI provides an agnostic, lightweight gateway that seamlessly ingests our Pydantic validation schemas. Its native support for `async`/`await` makes it robust for concurrent I/O prediction tasks, and its decoupled nature preserves our absolute separation of `src.api` from `src.ml` and `src.db`.

## Consequences
- **Positive**: Zero-config API documentation, massive performance boosts using ASGI/uvicorn, and deep alignment with modern Python static typing.
- **Negative**: Requires strict adherence to `async` best practices to avoid blocking the event loop on heavy ML compute tasks (which requires `run_in_threadpool`).
