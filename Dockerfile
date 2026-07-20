# Kissan AI — production image for Render / Docker
FROM python:3.10-slim

# System libs needed by faiss / numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python deps first (better layer cache)
COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir -r /workspace/backend/requirements.txt

# App code + static frontend (served by FastAPI)
COPY backend/ /workspace/backend/
COPY *.html /workspace/
COPY *.css /workspace/
COPY *.js /workspace/

WORKDIR /workspace/backend

# Pre-built FAISS index is copied with backend/data/vector_index.
# Only re-run ingest if the index is missing (saves long build + model download).
RUN if [ ! -f data/vector_index/index.faiss ] || [ ! -f data/vector_index/chunks.json ]; then \
      echo "Vector index missing — running ingest.py"; \
      python ingest.py; \
    else \
      echo "Vector index present — skipping ingest"; \
    fi

# Render injects PORT; default 8000 for local docker runs
ENV PORT=8000
ENV ENVIRONMENT=production
ENV AUTH_DEV_BYPASS=false
ENV FRONTEND_DIR=..

EXPOSE 8000

# Shell form so $PORT expands on Render
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
