# PostgreSQL Database Design

This document details the schema, entities, and scalability design for the FintechProject1 PostgreSQL database.

## 1. Business Entities

The platform revolves around several core entities:
*   **Loan**: The primary credit asset and point-in-time Applicant Snapshot.
*   **Payment**: Financial transactions towards a loan. Exists to calculate actual ROI and monitor repayment behavior.
*   **Marketing Campaign**: Targeted acquisition efforts. Exists to calculate Customer Acquisition Cost (CAC) and campaign ROI.
*   **Prediction**: Output of ML inference. Exists to preserve historical point-in-time risk scores for audit and model drift analysis.
*   **Model Version**: Tracks deployed ML models. Exists for governance, ensuring predictions can be traced back to exact algorithms and training datasets.
*   **Data Quality Report**: Stores metadata about ETL pipeline runs. Exists to track anomalous rows, missing value percentages, and quarantine events before data hits production.

## 2. Schema Design

### Table: `loans`
*   **Purpose**: Stores origination details, loan terms, current status, and the Applicant Snapshot.
*   **Primary Key**: `id`
*   **Foreign Keys**: `campaign_id` (Nullable, points to `marketing_campaigns`)
*   **Key Columns**: `loan_amnt`, `term`, `int_rate`, `grade`, `loan_status`, `annual_inc`, `home_ownership`, `addr_state`, `fico_range_low`, `fico_range_high`.
*   **Relationships**: 1:N with `payments`, 1:N with `predictions`.
*   **Indexes**: `id` (PK), `issue_d` (Time-series queries), `loan_status` (Filtering).
*   **Expected Volume**: ~2.5M rows.
*   **Update Frequency**: Medium (Status and outstanding balances updated monthly).

### Table: `payments`
*   **Purpose**: Ledger of all payment events against loans.
*   **Primary Key**: `payment_id` (Serial)
*   **Foreign Keys**: `loan_id` (points to `loans`)
*   **Key Columns**: `payment_date`, `amount_received`, `principal_portion`, `interest_portion`, `late_fee`.
*   **Relationships**: N:1 with `loans`.
*   **Indexes**: `payment_id` (PK), `loan_id` (FK), `payment_date` (Time-series aggregations).
*   **Expected Volume**: ~50M+ rows (assuming ~20-30 payments per loan).
*   **Update Frequency**: High (Inserted continuously/daily as payments clear).

### Table: `marketing_campaigns`
*   **Purpose**: Tracks acquisition channels and spend.
*   **Primary Key**: `campaign_id`
*   **Foreign Keys**: None.
*   **Key Columns**: `channel`, `spend`, `target_segment`, `start_date`, `end_date`.
*   **Relationships**: 1:N with `loans`.
*   **Indexes**: `campaign_id` (PK).
*   **Expected Volume**: ~100s to 1,000s rows.
*   **Update Frequency**: Very Low (Inserted when new campaigns launch).

### Table: `model_versions`
*   **Purpose**: Governance registry for deployed ML models.
*   **Primary Key**: `model_id`
*   **Foreign Keys**: None.
*   **Key Columns**: `model_name`, `version`, `algorithm`, `training_date`, `hyperparameters`, `is_active`.
*   **Relationships**: 1:N with `predictions`.
*   **Indexes**: `model_id` (PK), `is_active` (Filtering).
*   **Expected Volume**: ~10s to 100s rows.
*   **Update Frequency**: Very Low (Only upon new model deployment).

### Table: `predictions`
*   **Purpose**: Historical record of every risk score generated.
*   **Primary Key**: `prediction_id` (Serial)
*   **Foreign Keys**: `loan_id` (points to `loans`), `model_id` (points to `model_versions`).
*   **Key Columns**: `predicted_default_prob`, `assigned_grade`, `inference_timestamp`, `features_json`.
*   **Relationships**: N:1 with `loans`, N:1 with `model_versions`.
*   **Indexes**: `prediction_id` (PK), `loan_id` (FK), `inference_timestamp` (Monitoring).
*   **Expected Volume**: ~2.5M+ rows (one per application, plus subsequent behavioral scorings).
*   **Update Frequency**: High (Inserted during application flows or batch scoring).

### Table: `data_quality_reports`
*   **Purpose**: ETL metadata tracking.
*   **Primary Key**: `report_id` (Serial)
*   **Key Columns**: `pipeline_run_id`, `table_name`, `rows_processed`, `rows_quarantined`, `null_percentages`, `execution_timestamp`.
*   **Relationships**: Independent / Audit.
*   **Indexes**: `report_id` (PK), `execution_timestamp` (Sorting).
*   **Expected Volume**: ~10,000s rows.
*   **Update Frequency**: High (Inserted upon every pipeline completion).

## 3. Future Model Storage
Prediction results and machine learning artifacts must be handled carefully to ensure reproducibility and auditability.
*   **Versioning Strategy**: Handled by the `model_versions` table. Models are tagged with semantic versioning (v1.0.0). Predictions always reference `model_id`.
*   **Model Metadata**: The `hyperparameters` and feature lists are stored as JSONB to allow flexible auditing.
*   **Prediction History**: The `predictions` table acts as an append-only log. It stores `inference_timestamp` to determine exactly *when* the model made the decision.
*   **Feature Snapshots**: To prevent target leakage in audits, `features_json` in the `predictions` table captures the exact state of variables fed to the model at inference time.

## 4. Scalability Considerations
As the dataset grows (especially the `payments` table), the PostgreSQL architecture must scale:
*   **Partitioning**: The `payments` and `predictions` tables should be partition-by-range on `payment_date` and `inference_timestamp` (e.g., partitioned monthly). This allows fast querying of recent data and efficient dropping/archiving of old data.
*   **Indexes**: B-Tree indexes on all Foreign Keys to prevent slow JOINs. BRIN (Block Range Indexes) on partitioned time-series columns (`payment_date`) to minimize memory usage on massive tables.
*   **Archiving**: Data older than 7 years (regulatory threshold) will be moved to cold storage (e.g., Parquet in S3) and removed from live PostgreSQL partitions.
*   **Incremental Loads**: The ETL pipeline will use Upserts (`INSERT ON CONFLICT`) for `loans`, but strictly Append-Only logic for `payments` and `predictions` to ensure high throughput.
*   **Batch Processing**: Analytical views will heavily rely on materialized views updated nightly during off-peak hours, rather than computing aggregations on the fly for dashboards.

## 5. Implementation Notes
*   **Database Config**: Built using `pydantic-settings` to strictly type-check environment variables from `.env` with fallback defaults. The system transparently supports PostgreSQL in production and SQLite for local development (`use_sqlite=True`).
*   **SQLAlchemy 2.x Architecture**: Implemented `DeclarativeBase` for type-hinted ORM modeling. Connections are managed by a globally configured `Engine` and a `SessionLocal` factory.
*   **Thread-Safe Sessions**: Database sessions are vended through the `@contextmanager` pattern (`get_db_session()`), ensuring automatic `commit()`, rollback on exceptions, and guaranteed connection closure to prevent connection leaks.
*   **Alembic Integration**: Alembic's `env.py` dynamically injects the `database_url` directly from the `pydantic` configuration object. Migrations can be generated "offline" or "online" against the active PostgreSQL URL without hardcoding secrets in `alembic.ini`.
*   **Health Check**: Provided via `src.db.health.check_database_health()`, executing a standard connectivity ping on boot. All SQL actions invoke the unified `logging` framework.
