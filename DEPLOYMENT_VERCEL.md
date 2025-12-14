# 🚀 Deploying Static Frontend to Vercel

Since we want to host the frontend separately (Static HTML) and connect it to the Backend (Render), follow these steps.

---

## ✅ Prerequisites

1.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
2.  **Deployed Backend**: Ensure your backend is running on Render (e.g., `https://repository-mirror.onrender.com`).
3.  **CORS Configured**: The backend MUST have CORS enabled for the Vercel domain (We enabled `*` in `main.py`).

---

## 🛠️ Step 1: Prepare Frontend Code

We need to make the API URL dynamic instead of hardcoded to localhost.

1.  **Modify `static/index.html`** (or create a dedicated `frontend/` folder):
    *   Find the `fetch('/analyze')` call.
    *   Change it to use a full URL like `fetch('https://repository-mirror.onrender.com/analyze')`.
    *   *Better Approach*: Use a variable that you can swap easily.

    ```javascript
    // In your script tag
    const API_BASE_URL = "https://repository-mirror.onrender.com"; // Change this to your Render URL
    
    // ... inside analyzeRepo function
    const response = await fetch(`${API_BASE_URL}/analyze`, { ... });
    ```

2.  **Move Static Files**:
    *   It is recommended to move your HTML/CSS/JS into a separate folder, e.g., `frontend/`, if you are deploying them as a separate repo.
    *   If deploying from the **same** repo, you can point Vercel to the `static` directory.

---

## 🚀 Step 2: Deploy to Vercel

1.  **Dashboard**: Go to Vercel Dashboard -> **Add New Project**.
2.  **Connect Repo**: Select your `repository-mirror` repository.
3.  **Configure Project**:
    *   **Framework Preset**: Other (or just leave default).
    *   **Root Directory**: Click "Edit" and select `static` (since your index.html is there).
4.  **Deploy**: Click **Deploy**.

Vercel will give you a URL (e.g., `https://repository-mirror-frontend.vercel.app`).

---

## 🔗 Step 3: Verify Integration

1.  Open the Vercel URL.
2.  Open **Developer Tools (F12)** -> **Console** to watch for errors.
3.  Enter a GitHub Repo and click "Analyze".
4.  If you see a **CORS Error**:
    *   Check your Render logs.
    *   Confirm `main.py` has `allow_origins=["*"]` or specifically includes your Vercel domain.
    *   Redeploy the backend if needed.

---

## 🧪 Testing Production Integration

To test without deploying everything first:
1.  Run backend locally: `uvicorn main:app --port 8000`.
2.  Use a tunneling tool like **ngrok**: `ngrok http 8000`.
3.  Update your local HTML file to point to the `ngrok` URL (https).
4.  Open the HTML file directly in your browser.

This mimics a remote client talking to your server.
