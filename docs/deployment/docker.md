# Docker Deployment Architecture

The Fintech Analytics Platform utilizes a robust, multi-container Docker architecture capable of running identically in local development and production environments. All containers run natively using non-root configurations.

## 1. Architecture

*   **API Container**: Runs the FastAPI orchestration layer natively using `uvicorn` wrapped in a highly optimized Python 3.12 Slim image. It employs a multi-stage `.venv` build to utterly purge build-time bloat (like `build-essential` or temporary caches).
*   **PostgreSQL Container**: Runs standard `postgres:15` acting as the fully transactional persistence tier.
*   **Persistent Volumes**:
    *   `postgres_data`: Ensures data durability across PostgreSQL restarts or rebuilds.
    *   `model_registry`: Ensures compiled `.joblib` machine learning trees survive API container upgrades and scalings.

## 2. Configuration & Environment Variables

The entire platform achieves strictly 12-factor statelessness by injecting configurations natively via environment variables (`.env`). No passwords, ports, or secrets are hardcoded in the repository.

Important variables:
*   `DATABASE_URL`: SQLAlchemy Connection string mapping dynamically to PostgreSQL.
*   `USE_SQLITE`: Boolean flag allowing graceful local test fallbacks.
*   `LOG_LEVEL`: Configures native `stdout`/`stderr` logging outputs (no log files are written onto the disk).

## 3. Build & Run Instructions

### Production Execution
To start the services using the locked production profile (optimized images, no hot-reloading):

```bash
docker-compose up -d --build
```

### Local Development Execution
To start the services natively with host-directory volume mounts for immediate hot-reloading (without rebuilding images):

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## 4. Health Checks
The architecture utilizes explicit dependency orchestration to prevent startup crashes:
1.  The Database container executes `pg_isready` natively using standard PostgreSQL sockets.
2.  The API container forcibly blocks execution via `depends_on: condition: service_healthy` until PostgreSQL successfully boots and migrates.
3.  The API container executes native Python `urllib` checks targeting `/health` to ensure the ML registry and web loops are entirely responsive, circumventing the need to install external bloat like `curl`.
