# Architecture Documentation

## Data Contracts and Foundation
The data architecture of FintechProject1 relies on strict adherence to a defined data contract before data is ingested into analytical domains.

### Goal
Decouple data producers (e.g., CSV dumps, external APIs) from downstream analytics by enforcing rigid schemas and quality validations at the boundary layer.

### Core Components
1. **Business Entities Definition**: The analytical environment relies on clean entities (Customer, Loan, Payment, Campaign). Documented in `business_problem.md`.
2. **Data Dictionary**: The absolute source of truth for field definitions and types. Documented in `feature_dictionary.md`.
3. **Data Quality Specification**: Pre-ingestion validation rules. Data failing these rules is quarantined, ensuring only production-grade data reaches PostgreSQL and machine learning models. Documented in `dataset.md`.

By defining these boundaries, downstream components (FastAPI endpoints, Credit Risk Models, Tableau Dashboards) are protected from schema drift and anomalous values.
