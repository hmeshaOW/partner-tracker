# Partner Tracker

Full-stack business development dashboard and weekly log assistant.

## What It Does

- Syncs Microsoft Outlook email + calendar activity (via Microsoft Graph delegated token)
- Uses backend AI agents to classify interactions into business domains:
  - Digital Assets
  - Private Capital
  - Technology & Modernization
  - Quantum Technologies
  - Data & AI
  - Other
- Tags interactions as BFF/internal vs external partner/client using domain rules
- Produces weekly leadership-ready report drafts based on captured activity

## Architecture

- Frontend: React + TypeScript + Vite (`frontend/`)
- Backend: FastAPI + Python (`backend/`)
- AI/Agent Layer:
  - `domain_agent.py`: domain categorization
  - `relationship_agent.py`: BFF/external classification
  - `report_agent.py`: weekly narrative generation (OpenAI + fallback)

## Setup

### 1) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

### 2) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend runs on `http://localhost:8000`.

## Microsoft Graph Access

Provide a delegated Graph access token in the frontend input field before syncing.

Minimum Graph scopes expected:

- `Mail.Read`
- `Calendars.Read`
- `User.Read`

## Weekly Report Workflow

1. Paste Graph token
2. Click **Sync Email + Calendar**
3. Click **Generate Weekly Report**
4. Copy report and send to leadership distribution list

## Notes

- This implementation stores inferred activities in `backend/app/data/activities.json` for local development.
- Replace local storage with a secure database before production.
- Add proper Microsoft Entra app registration and OAuth flow for production usage.
