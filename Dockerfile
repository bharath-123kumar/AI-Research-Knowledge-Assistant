# Dockerfile for AI Research & Knowledge Assistant
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

WORKDIR /app

# Install system dependencies for PyMuPDF / OpenCV / C++ build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for layer caching
COPY requirements.txt .

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Pre-train ML model artifacts during Docker build stage to save startup RAM
RUN python -m src.ml.train_classifier

# Entrypoint: Start Uvicorn single worker to stay under 512MB RAM free tier limit
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
