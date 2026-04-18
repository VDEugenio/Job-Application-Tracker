# Setup Guide

## Prerequisites
- Python 3.11+
- Node 18+
- A Google account (your Gmail)
- An Anthropic API key

---

## Step 1 — Google Cloud Credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. "Job Tracker")
3. In the left menu go to **APIs & Services → Library**
4. Search for **Gmail API** and click **Enable**
5. Go to **APIs & Services → Credentials**
6. Click **Create Credentials → OAuth client ID**
7. Application type: **Desktop app** — name it anything
8. Click **Create**, then **Download JSON**
9. Rename the downloaded file to `credentials.json` and place it in the `backend/` folder

> First time you run the app and click "Connect Gmail", a browser window will open asking you to approve access. After approving, you'll be redirected back to the app automatically.

---

## Step 2 — Anthropic API Key

1. Get your key from [console.anthropic.com](https://console.anthropic.com)
2. In the `backend/` folder, copy `.env.example` to `.env`:
   ```
   cp backend/.env.example backend/.env
   ```
3. Open `backend/.env` and replace the placeholder with your real key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

---

## Step 3 — Run the Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Backend will be available at http://localhost:8001  
(Port 8000 is reserved for your other RAG API project.)

---

## Step 4 — Run the Frontend

In a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

---

## First Use

1. Open http://localhost:5173
2. Click **Connect Gmail** → approve in the browser → you'll be redirected back
3. Click **Sync Emails** — this fetches all emails from Feb 2026 onward and runs them through Claude
4. Applications detected appear in the table automatically
5. Use **+ Add** to manually add any that weren't detected
6. Click **Edit** on any row to update status or add notes

---

## Subsequent Uses

Just start both servers (Steps 3 & 4) and click **Sync Emails** whenever you want to check for new emails. The app skips emails it has already processed.
