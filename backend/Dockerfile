# Backend-only image (prefer root Dockerfile for full app + static/)
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# When building from monorepo root, use the root Dockerfile instead
# so ../static is available. This image expects FRONTEND_DIR override
# or a volume mount of static files.
ENV PORT=8000
ENV ENVIRONMENT=production
ENV AUTH_DEV_BYPASS=false
ENV FRONTEND_DIR=../static

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
