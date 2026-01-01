# Production Dockerfile for SymphAIny Backend
# Optimized for Cloud Run deployment

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including build deps for cryptography)
# Also includes OpenCV and Tesseract OCR dependencies for image processing
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy Poetry files first (for better caching)
COPY pyproject.toml poetry.lock* ./

# Copy validation script (needed before validation)
# Create scripts directory and copy the validation script
RUN mkdir -p scripts
COPY scripts/validate-poetry-lock.py scripts/

# Install Python dependencies using Poetry
# NOTE: poetry.lock should be committed and validated, not regenerated during build
# This ensures reproducible builds and catches dependency issues early
RUN poetry config virtualenvs.create false && \
    python3 scripts/validate-poetry-lock.py && \
    poetry install --no-interaction --no-ansi --no-root || \
    (echo "❌ poetry.lock is out of sync with pyproject.toml" && \
     echo "Please run 'poetry lock' locally and commit the updated file" && \
     exit 1)

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 symphainy && \
    chown -R symphainy:symphainy /app

USER symphainy

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8000

# Health check (using Python urllib.request - no curl dependency)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health').read()" || exit 1

# Run application
# Cloud Run provides PORT environment variable
CMD python3 main.py --host 0.0.0.0 --port ${PORT:-8000}




