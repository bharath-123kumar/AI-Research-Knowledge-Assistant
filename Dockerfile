# Dockerfile for AI Research & Knowledge Assistant
# Optimized for Render free tier (512MB RAM limit)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1

WORKDIR /app

# Install minimal system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install CPU-only PyTorch + project dependencies to minimize image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create necessary data directories
RUN mkdir -p data/raw_documents data/vector_db data/dataset models

# Pre-train ML classifier during image build so no RAM is consumed at runtime startup
RUN python -m src.ml.train_classifier

# Expose default port
EXPOSE 8000

# Start single Uvicorn worker — minimizes memory footprint on Render 512MB free tier
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 60"]
