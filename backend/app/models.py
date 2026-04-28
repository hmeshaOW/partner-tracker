from pydantic import BaseModel, Field
from typing import Literal


class SyncRequest(BaseModel):
    access_token: str = Field(min_length=20)


class InferredActivity(BaseModel):
    id: str
    source: Literal["email", "meeting"]
    title: str
    contact: str
    organization: str
    client: str
    domain: str
    summary: str
    date: str
    confidence: float
    is_bff: bool
    is_external: bool
    bff_status: str
    stage_hint: str
    next_step: str
    matched_opportunity_id: str | None = None


class SyncResponse(BaseModel):
    synced_items: int
    inferred_activities: list[InferredActivity]


class OpportunityRecord(BaseModel):
    opportunity_id: str
    client: str
    cit: str | None = None
    opportunity_name: str
    bff_status: str | None = None
    stage: str | None = None
    generating_partner: str | None = None
    hany_involvement_type: str | None = None
    hany_is_core_pursuit: bool | None = None
    fees_value: float | None = None
    fees_currency: str | None = None
    fees_value_usd: float | None = None
    probability: float | None = None
    industry_sector: str | None = None
    capability_teams: str | None = None
    opportunity_source: str | None = None
    country: str | None = None
    city_or_state: str | None = None
    estimated_start_date: str | None = None
    duration_weeks: int | None = None
    software_or_ai_involved: str | None = None
    created_on: str | None = None


class OpportunityListResponse(BaseModel):
    opportunities: list[OpportunityRecord]
    summary: dict


class WeeklyReportRequest(BaseModel):
    period_start: str
    period_end: str


class WeeklyReportResponse(BaseModel):
    period_start: str
    period_end: str
    report_markdown: str
    totals: dict


class CatalogService(BaseModel):
    name: str
    url: str


class CatalogServicesResponse(BaseModel):
    services: list[CatalogService]
