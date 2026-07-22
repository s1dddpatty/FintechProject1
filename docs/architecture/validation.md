# Validation Architecture

The Data Validation Engine is a foundational, reusable component designed to protect downstream layers (Analytics, Machine Learning, Dashboards) from erroneous data.

## 1. Validation Flow
The engine uses a pipeline composed of three distinct execution phases:
1.  **Schema Validation**: Verifies structural integrity (Column presence, Data Types, Primary Key uniqueness). If schema validation fails fundamentally (e.g. missing PK), the pipeline safely aborts to prevent downstream pandas exceptions.
2.  **Business Validation**: Executes domain-specific rules (e.g., "Loan Amount > 0"). This ensures data mathematically aligns with fintech requirements.
3.  **Quality Validation**: Scans for distribution anomalies (Null percentages, duplicate rows, IQR outliers). High anomalies trigger warnings rather than hard failures, allowing models to handle imputation.

## 2. Reusability and Clean Architecture
The architecture is data-source agnostic. Whether the dataframe is hydrated from a CSV reading script, queried from PostgreSQL via SQLAlchemy, or loaded from Parquet, the `ValidationPipeline` only expects a `pandas.DataFrame`.
The engine leverages `pydantic` to serialize the outcome into a JSON-friendly `ValidationReport`, which can be written to the `data_quality_reports` database table.

## 3. Supported Validation Rules
The `BusinessValidator` evaluates a list of `BusinessRule` instances. Standard rules include:
*   Positive loan amount
*   Valid interest rates (0-50%)
*   Valid term bounds
*   Positive annual income

## 4. Extending Validation Rules
To add a new business rule, simply define a new `BusinessRule` with a pandas vectorization lambda.

```python
from src.pipelines.validation import BusinessRule

new_rule = BusinessRule(
    name="Minimum Credit Score",
    check_func=lambda df: df['fico_range_low'] < 600 if 'fico_range_low' in df.columns else False,
    error_msg="FICO score must be at least 600."
)
```
Pass the rule into the `BusinessValidator` initialization to enforce it instantly.
