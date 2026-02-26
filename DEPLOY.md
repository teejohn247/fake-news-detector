# Deploy Fake News Detector on Render

**Running out of memory (512 MB) on Render?** → Use **Google Cloud Run** instead: see **[DEPLOY_GOOGLE_CLOUD.md](DEPLOY_GOOGLE_CLOUD.md)**. Cloud Run’s free tier allows **2 GB memory**, so BERT runs at no cost for moderate traffic.

---

## Prerequisites

- A [Render](https://render.com) account (free tier works for trying; BERT may need more RAM).
- Your code in a **Git repository** (GitHub, GitLab, or Bitbucket). Render deploys from Git.

---

## Fix: Push rejected (venv / model too large)

**You do not need to add the BERT model or `venv/` to the repo.** The app downloads `bert-base-uncased` from Hugging Face on first run. A `.gitignore` is included so `venv/` and `models/` are excluded.

If you already committed them and push was rejected, run this from your project folder:

```bash
cd fake-news-detector
# Undo the last commit but keep your files
git reset --soft HEAD~1
# Unstage the large folders (they are now in .gitignore)
git reset HEAD venv models 2>/dev/null || true
# Re-add everything (venv and models will be ignored)
git add .
git status   # Confirm venv/ and models/ are not listed
git commit -m "Initial commit (no venv or models)"
git push -u origin main
```

If you have more than one commit and the large files are in an older commit, use:

```bash
git rm -r --cached venv models 2>/dev/null || true
git add .
git commit -m "Stop tracking venv and models"
git push -u origin main
```

If the push still fails (history still has big files), you may need to remove them from history, e.g. with [git filter-repo](https://github.com/newren/git-filter-repo) or by creating a fresh repo and copying only the code (no `venv`, no `models`).

---

## Python version (required for build)

The repo includes a **`.python-version`** file set to **3.12.4**. Render uses this to select the Python version. **Do not remove it**—with Python 3.14, pandas and other packages would build from source and fail.

If a previous deploy used Python 3.14, clear the build cache so Render picks 3.12:
- In Render Dashboard → your service → **Settings** → **Build & Deploy** → **Clear build cache**, then trigger a new deploy.

---

## Option 1: Deploy from Render Dashboard (recommended)

### 1. Push your project to GitHub

If you haven’t already (and **do not** add `venv/` or `models/`—see `.gitignore`):

```bash
cd fake-news-detector
git init
git add .
git commit -m "Initial commit"
# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/fake-news-detector.git
git push -u origin main
```

### 2. Create a new Web Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** → **Web Service**.
3. Connect your GitHub (or GitLab/Bitbucket) if needed.
4. Select the **fake-news-detector** repository.
5. Use these settings:

| Field | Value |
|--------|--------|
| **Name** | `fake-news-detector` (or any name) |
| **Region** | Choose one (e.g. Oregon) |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 300 app:app` |

### 3. Plan and environment

- **Free** (512 MB RAM): Build may succeed, but loading BERT at startup often runs out of memory. You may see the app crash or time out.
- **Starter** (512 MB–2 GB) or higher: Recommended so the BERT model can load. In the service **Settings**, set **Instance Type** to a plan with at least **2 GB RAM** if available.

No environment variables are required for basic run. Render sets `PORT` for you.

### 4. Deploy

Click **Create Web Service**. Render will:

1. Clone your repo  
2. Run `pip install -r requirements.txt`  
3. Start the app with the gunicorn command above  

When the build finishes, your app will be at:

`https://fake-news-detector-XXXX.onrender.com`  
(URL is shown on the service page.)

---

## Option 2: Deploy using render.yaml (Blueprint)

If you added the included `render.yaml` to the repo:

1. In Render dashboard: **New +** → **Blueprint**.
2. Connect the **fake-news-detector** repo.
3. Render will read `render.yaml` and create the web service with the settings defined there.
4. Adjust **plan** (e.g. to **Starter** for more RAM) in the dashboard after creation if needed.

---

## Important notes

1. **Memory**  
   BERT and dependencies need roughly 1.5–2 GB RAM. Free tier often isn’t enough. Use a paid plan with at least 2 GB if the app keeps crashing at startup.

2. **Cold starts**  
   On free/starter, the app sleeps after inactivity. The first request after idle can take 30–60 seconds while the server and BERT load.

3. **Ephemeral disk**  
   Anything written to disk (e.g. `blockchain_records.json`, `models/fake-news-bert/`) is lost on redeploy or restart. For persistence you’d need a database or Render Disk (paid).

4. **Timeouts**  
   The start command uses `--timeout 300` so the first request (model load) has time to complete. If you still see timeouts, increase the **Request timeout** in the service **Settings** on Render.

---

## Quick reference: Start command

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 300 app:app
```

- `$PORT`: Set by Render; do not replace.
- `--workers 1`: One process to limit RAM use with BERT.
- `--timeout 300`: 5-minute timeout for long-running requests (e.g. first load).

After deployment, open your service URL and use the app as you do locally.
