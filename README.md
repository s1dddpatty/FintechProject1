# FintechProject1

## Project Overview
FintechProject1 is a production-style Customer Lifecycle & Credit Risk Analytics Platform designed for financial institutions. It provides a robust, scalable architecture for performing portfolio analytics, customer lifecycle management, risk monitoring, and decision support.

## Business Objective
To demonstrate the end-to-end workflow utilized by financial institutions, enabling data-driven decisions related to credit risk, customer churn, and portfolio health. The platform emphasizes maintainability, modularity, and best practices in data engineering and analytics.

## High-Level Architecture
The platform is built as a modular Python application, avoiding the common pitfalls of notebook-heavy workflows. The architecture is driven by centralized configuration, dynamic path resolution, and isolated modules handling specific parts of the analytical lifecycle (e.g., ingestion, cleaning, feature engineering, modeling, and API delivery).

## Folder Structure
```
FintechProject1/
├── config/         # Centralized configuration and path management
├── data/           # Raw, interim, processed, and export data
├── dashboard/      # BI and dashboard artifacts
├── docs/           # Project documentation and specifications
├── logs/           # Pipeline and application logs
├── models/         # Serialized ML models and artifacts
├── notebooks/      # Exploratory data analysis and prototyping
├── reports/        # Generated reports and analytical outputs
├── sql/            # SQL scripts for database operations
├── src/            # Core source code modules
│   ├── analytics/
│   ├── api/
│   ├── cleaning/
│   ├── database/
│   ├── features/
│   ├── ingestion/
│   ├── ml/
│   ├── utils/
│   ├── validation/
│   └── visualization/
└── tests/          # Unit and integration tests
```

## Technology Stack
- **Language**: Python 3.9+
- **Configuration**: YAML, Python `pathlib`, `python-dotenv`
- **Data Processing**: Pandas, NumPy, PyArrow
- **Database**: PostgreSQL (via SQLAlchemy)
- **API**: FastAPI
- **Formatting & Linting**: Black, Flake8, MyPy

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd FintechProject1
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your details.
   ```bash
   cp .env.example .env
   ```

## Development Principles
- **No Hardcoded Paths**: Always use `config/paths.py` to resolve directories dynamically.
- **Centralized Config**: Add configuration variables to `config/config.yaml` and access them via `config/settings.py`.
- **Proper Logging**: Use the utility in `src/utils/logger.py` rather than print statements.
- **Code Quality**: Ensure type hints and docstrings exist for all functions. Format code using `black` and validate types with `mypy`.

## Future Phases
- Data Ingestion & Transformation pipelines
- Customer Risk Feature Engineering
- Credit Risk Modeling
- Interactive Analytical Dashboards
- RESTful API for Model Serving
