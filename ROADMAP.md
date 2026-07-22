# Architectural Roadmap

This document outlines the high-level roadmap and architectural evolution planned for the Fintech Analytics Platform.

## Near-Term (0-6 Months)
- **OpenTelemetry Native Integration**: Replace our custom context tracing with OpenTelemetry SDK bindings to export spans to Jaeger/Zipkin.
- **Asynchronous Ingestion Pipeline**: Migrate the synchronous pandas data ingestion pipeline to Dask or Apache Beam for horizontal scaling of large batch processing.
- **Enhanced Feature Store**: Move from an in-memory Pandas mapping to an actual backed Feature Store (e.g., Feast).

## Mid-Term (6-12 Months)
- **Celery / RabbitMQ**: Introduce background task queues for asynchronous model training instead of executing it inside the HTTP request cycle.
- **Authentication & Authorization**: Integrate OAuth2 and granular Role-Based Access Control (RBAC) to secure endpoints.
- **Real-time Inference Support**: Optimize the PredictionPipeline to handle millisecond-latency streaming inference queries alongside batch inference.

## Long-Term (1+ Years)
- **Kubernetes Native Deployment**: Establish complete Helm charts spanning the backend API, Postgres, RabbitMQ, and Model Serving layers.
- **Model Drift Detection**: Integrate evidential alerting inside the analytics engine if live production distributions shift from training distributions.
