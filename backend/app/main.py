from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    CatalogServicesResponse,
    OpportunityListResponse,
    SyncRequest,
    SyncResponse,
    WeeklyReportRequest,
    WeeklyReportResponse,
)
from .services.graph_client import GraphClient, save_inferred
from .services.storage import read_activities
from .services.intelligence_pipeline import infer_from_events, infer_from_messages
from .agents.report_agent import generate_weekly_report
from .services.workbook_loader import build_opportunity_summary, load_opportunities
from .services.service_catalog import get_catalog_services


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
        opportunities = load_opportunities()
        inferred = infer_from_messages(messages, opportunities) + infer_from_events(events, opportunities)
        save_inferred(inferred)
        return SyncResponse(synced_items=len(messages) + len(events), inferred_activities=inferred)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Sync failed: {exc}") from exc


@app.get("/api/opportunities")
async def list_opportunities() -> OpportunityListResponse:
    opportunities = load_opportunities()
    return OpportunityListResponse(
        opportunities=opportunities,
        summary=build_opportunity_summary(opportunities),
    )


@app.get("/api/catalog/services")
async def list_catalog_services() -> CatalogServicesResponse:
    return CatalogServicesResponse(services=get_catalog_services())


@app.post("/api/reports/weekly")
async def weekly_report(payload: WeeklyReportRequest) -> WeeklyReportResponse:
    items = read_activities()
    opportunities = load_opportunities()
    filtered = [
        item for item in items
        if payload.period_start <= item.get("date", "") <= payload.period_end
    ]

    report = generate_weekly_report(filtered, opportunities, payload.period_start, payload.period_end)
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
