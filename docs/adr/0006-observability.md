# ADR 0006: Observability

## Status
Accepted

## Context
Monitoring enterprise applications requires deep tracing of latency, HTTP throughput, and domain-specific operations (e.g. Ingestion and Predictions). If metrics are coupled strictly inside HTTP router functions, background CLI workers or message brokers will execute silently.

## Decision
We implemented an Observability layer (`src.observability`) relying on Prometheus client and Python `contextvars` for correlation IDs. Rather than instrumenting HTTP endpoints, we wrapped the underlying Service classes with Python decorators (`@track_prediction`, `@track_ingestion`, `@track_db_query`).

## Consequences
- **Positive**: Telemetry emits naturally regardless of the consumer (FastAPI, Airflow DAGs, Celery).
- **Negative**: Decorators mask the original function definitions, slightly muddying stack traces during low-level debugging.
