# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Create a virtual environment to isolate dependencies cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Production Image
FROM python:3.12-slim

# Create a non-root user to avoid running the web server as root
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

# Copy the isolated virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

# Copy application code and ensure correct ownership
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config/ ./config/

# Initialize the Model Registry directory with correct permissions
RUN mkdir -p /app/models/registry && chown -R appuser:appuser /app/models/registry

# Switch execution to the non-root user
USER appuser

# Expose standard API port
EXPOSE 8000

# Start Uvicorn bound to 0.0.0.0
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
