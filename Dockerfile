# Use Python 3.12 slim image for smaller size and faster builds
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
# Prevents Python from buffering output
ENV PYTHONUNBUFFERED=1 \
    # Prevents pip from creating a cache directory
    PIP_NO_CACHE_DIR=1 \
    # Set pip to have minimal verbosity
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# - libpq-dev: for any potential postgres dependencies
# - build-essential: for building some Python packages from source
# - curl: for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install the CPU-only PyTorch wheel before resolving sentence-transformers.
# The default Linux PyPI wheel pulls CUDA/NVIDIA runtime dependencies.
RUN pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch==2.13.0+cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import fitz, sentence_transformers, torch; assert torch.version.cuda is None"

# Copy application code
COPY app/ ./app/

# Create writable directory for ChromaDB persistence
RUN mkdir -p vector_db && \
    chmod 755 vector_db

# Health check - uses the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose the API port
EXPOSE 8000

# Run the application with Uvicorn
# - --host 0.0.0.0: Listen on all interfaces
# - --port 8000: Use port 8000
# - --workers 1: Single worker (suitable for I/O-bound tasks; increase if needed)
# - app.api.main:app: Module path to FastAPI application
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
