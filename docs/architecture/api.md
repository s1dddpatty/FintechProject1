# REST API Architecture

The FastAPI orchestration layer acts as the unified, stateless gateway into the Fintech Analytics ecosystem. Crucially, it strictly wraps underlying operational modules without ever housing independent business logic inside router handlers.

## 1. Request Lifecycle
Incoming traffic inherently passes through `GZipMiddleware` (compressing large feature JSONs natively), `CORSMiddleware`, and a highly specialized `RequestContextMiddleware`. The context middleware injects unique `X-Request-ID` tracing headers and calculates HTTP execution times natively. This guarantees we can trace analytical logic flows directly down through validation layers and model inference blocks securely.

## 2. Routing Strategy
The API is horizontally sharded by strict functional boundaries:
*   `/health`: Application uptime checks. Confirming TCP/IP database socket connections and native model registry directory visibility.
*   `/ingestion/*`: HTTP gateways capable of safely unpacking CSVs and Parquets and dropping them structurally down the internal `IngestionPipeline` validator blocks.
*   `/analytics/*`: Safely surfacing aggregated database functions dynamically.
*   `/models` and `/prediction`: The operational inference layers running mathematical scoring securely by resolving UUID models dynamically inside standard containers.

## 3. Dependency Injection
Our routing layers avoid tight module coupling or database singletons. Instead of initializing `SessionLocal` mid-flight, all architectural endpoints inject instances declaring `Depends(get_db)` or `Depends(get_model_registry)`. This utterly isolates tests, allowing simple mocking strategies and ensuring flawless connection pool closing mechanically during request teardowns.

## 4. Error Handling Architecture
Instead of dumping `Exception` stack traces across the wire, all system failures are globally caught by `global_exception_handler`. Known semantic domain violations safely inherit from `FintechBaseException` and map gracefully to standard deterministic `HTTP 400` formats.
