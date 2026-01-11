FROM python:3.12-slim

# Metadata
LABEL maintainer="votre-email@example.com"
LABEL description="Churn Prediction Backend API"

WORKDIR /app

# Install system dependencies (needed for curl healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create necessary directories
RUN mkdir -p /app/processors /app/processors/models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
