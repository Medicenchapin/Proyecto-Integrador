FROM python:3.11-slim

# System setup (xgboost wheel still needs build-essential for native deps).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    XGB_MODEL_PATH=/app/models/xgb_sales.json \
    OLLAMA_BASE_URL=http://host.docker.internal:11434/api/generate

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
