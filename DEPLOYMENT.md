# CardioInsight — Deployment Guide

## Option 1: Run Locally (Development)

```bash
cd cardioinsight
bash run.sh
```
Open: http://localhost:5000

---

## Option 2: Deploy on Render.com (FREE — Recommended)

Render.com gives you a **free public URL** like `https://cardioinsight.onrender.com`

### Steps:
1. Create a free account at https://render.com
2. Click **New → Web Service**
3. Connect your GitHub repo (push the project to GitHub first)
4. Render auto-detects `render.yaml` — just click **Deploy**
5. Your live URL will be ready in ~3 minutes

### Push to GitHub first:
```bash
git init
git add .
git commit -m "Initial CardioInsight commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cardioinsight.git
git push -u origin main
```

---

## Option 3: Deploy on PythonAnywhere (FREE)

1. Sign up at https://www.pythonanywhere.com (free account)
2. Go to **Files** → Upload your entire cardioinsight folder as a zip
3. Open a **Bash console** and run:
```bash
cd cardioinsight
pip install -r requirements.txt --user
python generate_data.py
python train_model.py
python charts.py
```
4. Go to **Web** tab → Add new web app → Flask → Python 3.10
5. Set **Source code**: `/home/yourusername/cardioinsight`
6. Set **WSGI file** to point to your `wsgi.py`
7. Click **Reload** — your app is live!

---

## Option 4: Deploy on Railway (FREE tier)

1. Sign up at https://railway.app
2. New Project → Deploy from GitHub
3. Add environment variable: `SECRET_KEY` = any random string
4. Railway auto-detects `Procfile` and runs:
   `gunicorn app:app`

---

## Option 5: Firebase (Original Plan — Static + Cloud Run)

Firebase Hosting alone only works for static sites.
For a Flask app, you need **Firebase + Cloud Run**:

```bash
# Install Firebase CLI
npm install -g firebase-tools
firebase login

# Build Docker image (requires Docker Desktop)
gcloud run deploy cardioinsight \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Recommendation**: Use Render.com instead — it's simpler and completely free.

---

## Admin Account

To access the admin panel at `/admin`, register with this email:
```
Email:    admin@cardioinsight.com
Password: (any password you choose)
```
Then visit: `http://localhost:5000/admin`

---

## Environment Variables (for production)

| Variable    | Value                | Description          |
|-------------|----------------------|----------------------|
| SECRET_KEY  | (random 32 chars)    | Flask session secret |
| FLASK_ENV   | production           | Disables debug mode  |

```bash
# Generate a secure secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```
