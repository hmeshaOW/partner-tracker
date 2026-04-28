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
    domain: str
    summary: str
    date: str
    confidence: float
    is_bff: bool
    is_external: bool


class SyncResponse(BaseModel):
    synced_items: int
    inferred_activities: list[InferredActivity]


class WeeklyReportRequest(BaseModel):
    period_start: str
    period_end: str


class WeeklyReportResponse(BaseModel):
    period_start: str
    period_end: str
    report_markdown: str
    totals: dict
