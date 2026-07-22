# Continuous Integration (CI)

This document outlines the Continuous Integration (CI) pipeline implemented for the Fintech Analytics Project using GitHub Actions.

## Workflow Overview

The CI pipeline automatically validates every code change to ensure production-grade quality, testing validity, security, and containerization stability. 

**Triggers**:
- `push`: Triggered on `main`, `develop`, and `feature/*` branches.
- `pull_request`: Triggered on `main` and `develop` branches.

## Jobs

The pipeline is intentionally modularized into four isolated jobs. This prevents one failure from short-circuiting unrelated verifications (e.g., a static type warning won't block the security audit).

### 1. Static Analysis
- **Purpose**: Validates code quality, styling, and type consistency.
- **Commands**: 
  - `ruff check src tests`
  - `mypy src tests`
- **Quality Gates**: Both Ruff (formatting/linting) and MyPy (static typing) must pass with 0 errors. The `if: always()` condition ensures MyPy executes even if Ruff fails.

### 2. Testing
- **Purpose**: Runs the functional and integration test suites and measures code coverage.
- **Commands**: 
  - `pytest --cov=src --cov-report=xml --cov-report=html --junitxml=pytest-results.xml`
- **Quality Gates**: All tests must pass. 

### 3. Docker
- **Purpose**: Verifies that the complete application and its infrastructure compile securely within the container runtime environment.
- **Commands**: 
  - `docker build -t fintech-app:ci-test .`
- **Quality Gates**: The multi-stage `Dockerfile` must successfully complete its build sequence. No images are pushed to registries during CI.

### 4. Security
- **Purpose**: Audits the python dependencies for known vulnerabilities and exploits.
- **Commands**: 
  - `pip install pip-audit`
  - `pip-audit -r requirements.txt -f json -o pip-audit-report.json`
- **Quality Gates**: Must detect 0 known vulnerabilities across all installed packages.

## Artifacts

Artifacts are automatically captured and uploaded on every run (including failures):
- **coverage-html**: Full HTML coverage report (`htmlcov/`).
- **coverage-xml**: Machine-readable coverage data (`coverage.xml`).
- **pytest-results**: Standardized JUnit test results (`pytest-results.xml`).
- **pip-audit-report**: JSON report containing vulnerability audit results (`pip-audit-report.json`).

## Caching Strategy

The workflow utilizes the standard `actions/setup-python@v5` with `cache: 'pip'`. This optimizes execution time by caching the pip download directories natively between runs based on a hash of the `requirements.txt`.

## Codecov Integration
For coverage tracking across branches, integrate Codecov into your CI workflow by appending the Codecov GitHub Action:
```yaml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```
This requires configuring the `CODECOV_TOKEN` repository secret.
