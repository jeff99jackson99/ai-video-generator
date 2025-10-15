# Multi-stage Dockerfile for AI Video Generator

# Stage 1: Base with system dependencies
FROM python:3.11-slim as base

# Install system dependencies for video/audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Stage 3: Runtime
FROM base as runtime

COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

COPY src/ /app/src/
COPY .env.example /app/.env.example

# Create data directories
RUN mkdir -p /app/data/media /app/data/voiceovers /app/output

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/healthz')"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.app.web:app", "--host", "0.0.0.0", "--port", "8000"]

