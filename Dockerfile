# Fake News Detector - for Google Cloud Run (needs ~2GB RAM for BERT)
FROM python:3.12-slim

WORKDIR /app

# Build tools + C lib headers for packages that compile C extensions (e.g. lru-dict)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install torch CPU-only first (Cloud Run has no GPU; avoids ~3GB CUDA deps)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Rest of deps (skip torch line so we keep CPU-only torch; PyPI would pull CUDA)
COPY requirements.txt .
RUN grep -v '^torch' requirements.txt > /tmp/req.txt && pip install --no-cache-dir -r /tmp/req.txt

# App code
COPY . .

# Pre-download BERT so the container does not need Hugging Face at runtime (fixes "Can't load tokenizer")
ENV BERT_PRETRAINED_PATH=/app/models/bert-base-uncased
RUN mkdir -p /app/models/bert-base-uncased && python -c "\
from transformers import BertTokenizer, BertForSequenceClassification; \
p='/app/models/bert-base-uncased'; \
BertTokenizer.from_pretrained('bert-base-uncased').save_pretrained(p); \
BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2).save_pretrained(p); \
print('BERT saved to', p); \
"

# Cloud Run sets PORT (default 8080)
ENV PORT=8080
EXPOSE 8080

# One worker to limit RAM; long timeout for first request (model load)
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 300 app:app
