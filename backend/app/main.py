from __future__ import annotations

from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    SyncRequest,
    SyncResponse,
    WeeklyReportRequest,
    WeeklyReportResponse,
)
from .services.graph_client import GraphClient, save_inferred
from .services.storage import read_activities
from .services.intelligence_pipeline import infer_from_events, infer_from_messages
from .agents.report_agent import generate_weekly_report


app = FastAPI(title="Partner Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/sync", responses={400: {"description": "Sync failure"}})
async def sync_data(payload: SyncRequest) -> SyncResponse:
    try:
        client = GraphClient(payload.access_token)
        messages = await client.fetch_messages(limit=40)
        events = await client.fetch_events(limit=20)
        inferred = infer_from_messages(messages) + infer_from_events(events)
        save_inferred(inferred)
        return SyncResponse(synced_items=len(messages) + len(events), inferred_activities=inferred)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Sync failed: {exc}") from exc


@app.post("/api/reports/weekly")
async def weekly_report(payload: WeeklyReportRequest) -> WeeklyReportResponse:
    items = read_activities()
    filtered = [
        item for item in items
        if payload.period_start <= item.get("date", "") <= payload.period_end
    ]

    report = generate_weekly_report(filtered, payload.period_start, payload.period_end)
    totals = {
        "activities": len(filtered),
        "external_activities": sum(1 for x in filtered if x.get("is_external")),
        "bff_activities": sum(1 for x in filtered if x.get("is_bff")),
    }

    return WeeklyReportResponse(
        period_start=payload.period_start,
        period_end=payload.period_end,
        report_markdown=report,
        totals=totals,
    )
