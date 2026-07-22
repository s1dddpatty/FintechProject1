# Business Analytics Engine

The Analytics Layer acts as the computational engine for the Fintech Platform. It is fully decoupled from both the web API (FastAPI) and the downstream visualization dashboarding software.

## 1. Architecture
The architecture strictly follows a Service pattern dependent on SQLAlchemy. Instead of running memory-intensive Pandas aggregations locally, the engine leverages SQLAlchemy `func` calls to push aggregation logic down into the PostgreSQL database. This ensures analytical queries naturally scale to massive row volumes.

*   **PortfolioAnalytics**: Computes macroscopic KPIs (Total Volume, Yield, Global Default Rate).
*   **CustomerAnalytics**: Slices demographic data (Geographic distributions, Income statistics).
*   **LoanAnalytics**: Analyzes credit origination trends (Grades, Terms, Status).
*   **RiskAnalytics**: Executes cross-entity JOINs to calculate conditional probabilities (Default Rate by State, Grade, etc.).
*   **MarketingAnalytics**: Tracks pipeline acquisition costs.
*   **ExecutiveAnalytics**: Orchestrates the sub-modules into a unified `ExecutiveDashboardReport`.

## 2. Metric Definitions
Metrics are strictly typed using Pydantic classes (`MetricValue`, `AggregateMetric`) rather than raw dictionaries. This ensures that any upstream consumer has a guaranteed schema.
*   `MetricValue`: A single scalar metric (e.g., Average Interest Rate = 12.5%).
*   `AggregateMetric`: A distribution or grouping (e.g., Loan Count by Grade).

## 3. Extension Strategy
To add a new metric:
1. Define the SQL aggregation inside the relevant domain class (e.g., `RiskAnalytics`).
2. Return a strictly typed `AggregateMetric` or `MetricValue`.
3. If it's a critical KPI, append it to `ExecutiveAnalytics.generate_executive_summary()` to automatically surface it to the leadership dashboards.
