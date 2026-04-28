# Partner Tracker

Full-stack business development dashboard and weekly log assistant.

## What It Does

- Loads the opportunity register from `documentation/Hany Opportunities Reporting.xlsx` and uses it as the starting opportunity data model
- Syncs Microsoft Outlook email + calendar activity from the signed-in user's Graph token
- Uses backend AI agents and LLM extraction to convert emails and calendar events into structured BD log entries
- Classifies interactions into business domains:
  - Digital Assets
  - Private Capital
  - Technology & Modernization
  - Quantum Technologies
  - Data & AI
  - Other
- Tags interactions as BFF/internal vs external partner/client using domain rules
- Matches inferred activity back to workbook opportunities where possible
- Produces weekly leadership-ready report drafts based on captured activity and the workbook-backed pipeline

## Architecture

- Frontend: React + TypeScript + Vite (`frontend/`)
- Backend: FastAPI + Python (`backend/`)
- AI/Agent Layer:
  - `domain_agent.py`: domain categorization
  - `relationship_agent.py`: BFF/external classification
  - `log_entry_agent.py`: LLM extraction of BD log entries from Graph content
  - `report_agent.py`: weekly narrative generation (OpenAI + fallback)
- Workbook Loader:
  - `workbook_loader.py`: parses the Excel opportunity register and computes pipeline summary metrics

## Setup

### 1) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs on `http://localhost:5173`.

Frontend `.env` values:

- `VITE_API_BASE_URL`
- `VITE_ENTRA_CLIENT_ID`
- `VITE_ENTRA_TENANT_ID`
- `VITE_ENTRA_REDIRECT_URI`

See `documentation/entra-app-registration.md` for the exact Entra SPA configuration and CLI commands.

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

Backend `.env` values:

- `OPENAI_API_KEY` and `OPENAI_MODEL` for direct OpenAI usage
- `LENAI_API_BASE_URL`, `LENAI_API_KEY`, and `LENAI_MODEL` for LenAI/OpenAI-compatible internal API routing
- `OPPORTUNITIES_WORKBOOK_PATH` to point at the Excel opportunity register

LLM routing precedence:

1. If `LENAI_API_BASE_URL`, `LENAI_API_KEY`, and `LENAI_MODEL` are set, backend agents use LenAI endpoint.
2. Otherwise, backend falls back to direct OpenAI via `OPENAI_API_KEY` and `OPENAI_MODEL`.

## Microsoft Graph Access

Provide a delegated Graph access token in the frontend input field before syncing.

Minimum Graph scopes expected:

- `Mail.Read`
- `Calendars.Read`
- `User.Read`

The frontend supports Microsoft sign-in through MSAL when the Entra settings above are provided. A manual token paste fallback remains available.

If your tenant blocks self-service app registration, use the manual admin-assisted setup documented in `documentation/entra-app-registration.md`.

## Weekly Report Workflow

1. Paste Graph token
2. Or sign in with Microsoft from the frontend
3. Click **Sync Email + Calendar**
4. Review the extracted log entries and workbook opportunity register
5. Click **Generate Weekly Report**
6. Copy report and send to leadership distribution list

## Notes

- This implementation stores inferred activities in `backend/app/data/activities.json` for local development.
- Opportunity seed data is read directly from `documentation/Hany Opportunities Reporting.xlsx`.
- Replace local storage with a secure database before production.
- Add a formal Microsoft Entra app registration with approved redirect URIs and delegated Graph permissions before production usage.
