# 🚀 Deploying Repository Mirror to Render

This guide provides step-by-step instructions to deploy the Repository Mirror backend to **Render**, a unified cloud platform.

---

## ✅ Prerequisites

1.  **GitHub Account**: Ensure this project is pushed to a GitHub repository.
2.  **Render Account**: Sign up at [render.com](https://render.com).
3.  **GitHub Token**: You will need your `GITHUB_TOKEN` ready for the environment variables.

---

## 🛠️ Method 1: Deploy from Git (Manual Setup)

This is the easiest way for single services.

1.  **Dashboard**: Go to your Render Dashboard and click **New +** -> **Web Service**.
2.  **Connect Repo**: Select "Build and deploy from a Git repository" and choose your `repository-mirror` repo.
3.  **Configure Details**:
    *   **Name**: `repository-mirror`
    *   **Region**: Closest to you (e.g., Singapore, Frankfurt, Oregon).
    *   **Branch**: `main` (or master).
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:10000`
4.  **Environment Variables**:
    *   Click **Advanced** -> **Add Environment Variable**.
    *   Key: `GITHUB_TOKEN`
    *   Value: `your_github_token_here` (Copy from your local .env, ensuring no spaces).
5.  **Deploy**: Click **Create Web Service**.

Render will start building your app. It normally takes 2-3 minutes.

---

## 📄 Method 2: Infrastructure as Code (Blueprint)

This method uses the `render.yaml` file included in this project for automatic configuration.

1.  **Dashboard**: Go to Render Dashboard and click **New +** -> **Blueprint**.
2.  **Connect Repo**: Connect your `repository-mirror` repository.
3.  **Service Name**: Render will automatically detect the `repository-mirror` service defined in `render.yaml`.
4.  **Updates**: Click **Apply**.
5.  **Secrets**: You will be prompted to enter value for `GITHUB_TOKEN` since `sync: false` is set in the yaml. Enter your token securely here.

---

## ⚠️ Common Deployment Pitfalls & Fixes

### 1. **"Port binding failed" or "App crashed"**
*   **Cause**: The app is trying to listen on a different port than Render expects, or `127.0.0.1` instead of `0.0.0.0`.
*   **Fix**: Ensure the start command binds to `0.0.0.0`. Render sets a `PORT` env var (default 10000). The command used above (`-b 0.0.0.0:10000`) correctly handles this.

### 2. **"ModuleNotFound: gunicorn"**
*   **Cause**: `gunicorn` was not added to `requirements.txt`.
*   **Fix**: Ensure `requirements.txt` includes `gunicorn`. I have already added this for you.

### 3. **Rate Limiting Errors (403)**
*   **Cause**: The `GITHUB_TOKEN` environment variable is missing or invalid on Render.
*   **Fix**: Go to the service **settings** -> **Environment** and verify `GITHUB_TOKEN` is set correctly.

### 4. **Static Files 404**
*   **Cause**: Issues resolving the path to the `static` folder in a production environment.
*   **Fix**: The `app.mount("/static", ...)` code works relatively to the working directory. Ensure the `static/` folder is committed to Git.

---

## 📡 Accessing the API

Once deployed, Render will provide a URL (e.g., `https://repository-mirror.onrender.com`).
*   **UI**: Visit `https://repository-mirror.onrender.com`
*   **Docs**: Visit `https://repository-mirror.onrender.com/docs`
