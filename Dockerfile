FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt
COPY . .
RUN mkdir -p data/logs data/knowledge_base qdrant_storage
EXPOSE 8000
CMD ["uvicorn", "ui.api:app", "--host", "0.0.0.0", "--port", "8000"]
