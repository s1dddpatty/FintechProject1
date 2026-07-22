# Observability and Operational Readiness

This document outlines the observability layer for the Fintech Analytics project. The layer ensures production readiness by tracking performance, tracking exceptions, establishing system probes, and collecting metrics without altering core business logic.

## Structured Logging
All system logs are structured as JSON via a custom `StructuredJsonFormatter` replacing the standard formatting.

Every incoming HTTP request intercepts the context to attach the following structured fields:
- `timestamp`
- `request_id` (Correlation ID)
- `path`
- `method`
- `status_code`
- `processing_time`
- `exception` (In case of a traceback)

This allows centralized log aggregators (e.g., ELK, Datadog, Splunk) to parse, filter, and trace metrics effectively.

## Prometheus Metrics
The application exposes Prometheus metrics at `/metrics` using the `prometheus_client`.

### Available Metrics:
- **HTTP Metrics**:
  - `http_request_count` (Counter): Total HTTP requests labeled by method, endpoint, and status.
  - `http_request_duration_seconds` (Histogram): Request latency labeled by method and endpoint.
  - `active_requests` (Gauge): Current concurrent requests.
  - `failed_requests_total` (Counter): Failed requests (>= 400).

- **Business Performance Metrics**:
  - `prediction_count_total` (Counter): Total predictions.
  - `prediction_latency_seconds` (Histogram): Prediction execution time.
  - `prediction_failures_total` (Counter): Prediction errors.
  - `ingestion_count_total` (Counter): Total batch ingestions.
  - `ingestion_duration_seconds` (Histogram): Ingestion execution time.
  - `validation_failures_total` (Counter): Total data validation failures.

- **System & Error Metrics**:
  - `db_query_duration_seconds` (Histogram): Database query duration labeled by operation (e.g., `get_by_id`, `add`).
  - `exceptions_total` (Counter): Exceptions captured, labeled by `exception_type`.

## System Probes

### 1. Health (`/health`)
Returns comprehensive operational metadata, diagnosing platform components dynamically:
- `database`: PostgreSQL connectivity state.
- `registry`: Local model registry availability.
- `disk_usage_percent`: Percentage of free disk space in the deployment directory.
- `memory_usage_percent`: RAM utilization retrieved natively via `psutil`.
- `uptime_seconds`: Running span of the current application process.
- `build`: Build metadata (git commit, build time, Python version, environment).

### 2. Liveness (`/live`)
A simple, lightweight probe (returning `{"status": "alive"}`) used by container orchestrators (e.g., Kubernetes, Docker Swarm) to determine if the container runtime is up and capable of accepting traffic.

### 3. Readiness (`/ready`)
A dependency-aware probe used to check if the application is ready to serve active traffic. It asserts database connectivity and the presence of critical directories (like the Model Registry). If any critical resource is down, it returns `{"status": "not_ready"}`.

## Tracing & Correlation IDs
A `correlation_id` is automatically injected at the network edge inside `ObservabilityMiddleware`. 

The Context is preserved globally using Python's `contextvars`, making the correlation ID instantly retrievable across any asynchronous boundary. The `X-Request-ID` is returned in every HTTP response header.

### Future OpenTelemetry Integration
The current `contextvars` correlation strategy natively aligns with OpenTelemetry specifications. In the future, by installing the OpenTelemetry SDK (`opentelemetry-api` and `opentelemetry-sdk`), we can seamlessly inject spans directly into this correlation context. No routing rewrites will be necessary, as the service layers are already decorated and abstracted independently from the API gateways.
