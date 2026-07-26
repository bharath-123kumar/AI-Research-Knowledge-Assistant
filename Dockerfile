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

# Ensure storage directories exist
RUN mkdir -p data/raw_documents data/vector_db data/dataset models

# Expose server port
EXPOSE 8000

# Entrypoint: Train ML model if missing, then start production Uvicorn server
CMD ["sh", "-c", "python -m src.ml.train_classifier && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2"]
