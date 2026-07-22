# Persistence & Loading Architecture

The Loading Layer safely persists validated `pandas.DataFrames` into the PostgreSQL analytical data model using SQLAlchemy 2.x. 

## 1. Architecture Flow
The ingestion relies on a robust three-stage translation process to decouple raw dataframe operations from database semantics.

1. **Mapping (`DataFrameMapper`)**: Acts as an Anti-Corruption Layer. It absorbs raw Pandas logic (e.g., swapping `np.nan` -> `None` for SQL compatibility) and converts rows directly into SQLAlchemy 2.x ORM models (`Customer`, `Loan`, etc.). The mapper itself possesses zero database engine awareness.
2. **Repository Pattern (`src/db/repositories/`)**: Each business entity gets a dedicated CRUD repository (e.g., `CustomerRepository`). This isolates SQLAlchemy specific querying and session management away from the pipelines.
3. **Batch Loader (`BatchLoader`)**: Takes a list of instantiated ORM models and executes bulk insertion with robust transaction protection.

## 2. Transaction Strategy
PostgreSQL insertions happen in user-defined `chunk_size` blocks (default 1000) using `session.flush()`. This keeps Python memory utilization extremely low while maximizing DB connection throughput for million-row datasets.

Crucially, **the entire payload commits in a single transaction**. If `chunk 8 of 10` violates a primary key constraint or null-rule, a `SQLAlchemyError` is caught, the entire 10-chunk batch triggers `session.rollback()`, and the database is reverted to its pure pre-job state. This guarantees we never end up with half-loaded corrupted CSV ingestions in production.

## 3. Extension
By relying on the `DeclarativeBase` ORM mapping, any new dataset table can be supported immediately by writing a new entity class in `src/db/models.py` and extending the `BaseRepository[T]` generic type.
