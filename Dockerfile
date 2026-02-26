# Fake News Detector - for Google Cloud Run (needs ~2GB RAM for BERT)
FROM python:3.12-slim

WORKDIR /app

# Install deps (no build tools needed for wheels on 3.12)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .
# Cloud Run sets PORT (default 8080)
ENV PORT=8080
EXPOSE 8080

# One worker to limit RAM; long timeout for first request (model load)
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 300 app:app
