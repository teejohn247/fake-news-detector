# Deploy Fake News Detector on Google Cloud Run (free tier)

Cloud Run gives you **enough memory for BERT** (2 GB) and a **generous free tier**, so you can run this app at no cost for moderate use.

## Why Cloud Run for free?

- **Render free tier** = 512 MB RAM → BERT needs ~2 GB → **out of memory**.
- **Cloud Run free tier** (request-based):
  - **2 million requests/month**
  - **360,000 GiB-seconds** (e.g. 2 GB × 50 hours)
  - **180,000 vCPU-seconds**
- You set **memory to 2 GiB** per instance. BERT loads; you stay within free tier for normal traffic.

---

## Prerequisites

1. **Google Cloud account** – [console.cloud.google.com](https://console.cloud.google.com).
2. **Billing enabled** – Free tier still requires a billing account; you won’t be charged until you exceed free limits. Set a **budget alert** (e.g. $5) in Billing to avoid surprises.
3. **gcloud CLI** (optional but recommended) – [Install the Google Cloud CLI](https://cloud.google.com/sdk/docs/install).

---

## 1. Create a project and enable APIs

```bash
# Create a project (or pick an existing one)
gcloud projects create fake-news-detector-PROJECT_ID --name="Fake News Detector"

# Or use existing project
export PROJECT_ID=your-existing-project-id

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## 2. Build and deploy from your machine (no Docker locally)

From the **fake-news-detector** directory:

```bash
cd /path/to/fake-news-detector

# Build the container image in the cloud and deploy to Cloud Run
gcloud run deploy fake-news-detector \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --allow-unauthenticated \
  --timeout 300
```

- **`--source .`** – Builds from the Dockerfile in the current directory (Cloud Build runs in GCP).
- **`--memory 2Gi`** – Required for BERT; fits within free tier.
- **`--min-instances 0`** – Scale to zero when idle (saves cost).
- **`--timeout 300`** – 5 minutes so the first request (model load) can finish.
- **`--allow-unauthenticated`** – Public HTTP access. Omit if you want only logged-in users.

When prompted, choose a region (e.g. **us-central1**). When asked “Allow unauthenticated invocations?”, answer **y**.

After deploy, you’ll get a URL like:

`https://fake-news-detector-XXXXX-uc.a.run.app`

---

## 3. Deploy using Docker (build image locally)

If you prefer to build the image yourself:

```bash
cd /path/to/fake-news-detector

# Configure Docker for GCP
gcloud auth configure-docker

# Build (replace PROJECT_ID and REGION)
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
docker build -t gcr.io/${PROJECT_ID}/fake-news-detector .

# Push
docker push gcr.io/${PROJECT_ID}/fake-news-detector

# Deploy
gcloud run deploy fake-news-detector \
  --image gcr.io/${PROJECT_ID}/fake-news-detector \
  --region ${REGION} \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 0 \
  --timeout 300 \
  --allow-unauthenticated
```

---

## 4. Deploy from GitHub (CI/CD)

1. In [Cloud Console](https://console.cloud.google.com): **Cloud Build** → **Triggers**.
2. **Create trigger** → Source: **GitHub** (connect repo) → select **fake-news-detector**.
3. **Configuration**: “Dockerfile” → set **Dockerfile location** to `Dockerfile`.
4. **Substitution variables** (optional): `_REGION=us-central1`.
5. After the trigger runs, deploy the built image to Cloud Run (or add a second step in the trigger to deploy).

You can also use **Cloud Build** with a `cloudbuild.yaml` that builds and deploys in one pipeline.

---

## Free tier and cost

- **Free each month**: 2M requests, 360K GiB-seconds, 180K vCPU-seconds (e.g. us-central1).
- With **2 GiB** and **min-instances 0**, light/moderate traffic usually stays at **$0**.
- Set a **budget** in Billing (e.g. $5) and an email alert so you’re notified if usage grows.

---

## Cold starts

With **min-instances 0**, the first request after idle can take **30–90 seconds** while the container starts and BERT loads. Later requests are fast. For always-on (no cold start), set **min-instances 1** (uses paid time when idle).

---

## Optional: heuristic-only mode for 512 MB (e.g. Render)

If you want to stay on Render’s 512 MB free tier and don’t need BERT, you can add an env var (e.g. `HEURISTIC_ONLY=1`) and in the app skip loading BERT and use only the heuristic. That would require a small code change; ask if you want this.

---

## Quick reference

| Item        | Value |
|------------|--------|
| Memory     | **2 GiB** (required for BERT) |
| Region     | **us-central1** (free tier) |
| Timeout    | **300 s** |
| Start cmd  | `gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 300 app:app` |

The repo’s **Dockerfile** and **.dockerignore** are set up for this. No need to add `venv/` or `models/`; the app downloads BERT from Hugging Face at startup.
