from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from ..config import settings
from .domain_agent import classify_domain
from .relationship_agent import classify_relationship


SYSTEM_PROMPT = """You extract business-development log entries from Outlook emails and calendar events.
Use the provided opportunity register to infer likely client, BFF status, stage hints, and next steps.
Return compact JSON only with shape: {\"entries\": [{...}]}. Each entry must include source_id, source, title, contact, organization, client, domain, summary, date, confidence, is_bff, is_external, bff_status, stage_hint, next_step, matched_opportunity_id.
If a field is unknown, use empty string or null. Do not invent fees or values.
"""


def _get_item_core(item: dict[str, Any]) -> tuple[str, str, str]:
    subject = item.get("title") or item.get("subject") or ""
    body = item.get("summary") or item.get("body_preview") or ""
    contact = item.get("contact") or item.get("primary_contact") or "unknown@unknown"
    return subject, body, contact


def _match_opportunity(subject: str, body: str, organization: str, opportunities: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str]:
    lowered = f"{subject} {body}".lower()
    for opportunity in opportunities:
        client_name = str(opportunity.get("client") or "")
        opportunity_name = str(opportunity.get("opportunity_name") or "")
        if client_name and client_name.lower() in lowered:
            return opportunity, client_name
        if opportunity_name and opportunity_name.lower() in lowered:
            return opportunity, client_name or organization
    return None, organization


def _resolve_bff_status(matched: dict[str, Any] | None, is_bff: bool) -> str:
    default_status = "Internal" if is_bff else "Prospect"
    if not matched:
        return default_status
    return matched.get("bff_status") or default_status


def _fallback_extract(item: dict[str, Any], opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    subject, body, contact = _get_item_core(item)
    is_bff, is_external, organization = classify_relationship(contact)
    domain, confidence = classify_domain(f"{subject} {body}")
    matched, client = _match_opportunity(subject, body, organization, opportunities)
    bff_status = _resolve_bff_status(matched, is_bff)
    stage_hint = matched.get("stage") if matched else None

    return {
        "source_id": item.get("id") or item.get("source_id") or "",
        "source": item.get("source") or "email",
        "title": subject,
        "contact": contact,
        "organization": organization,
        "client": matched.get("client") if matched else client,
        "domain": domain,
        "summary": body[:220],
        "date": item.get("date") or "",
        "confidence": confidence,
        "is_bff": is_bff,
        "is_external": is_external,
        "bff_status": bff_status,
        "stage_hint": stage_hint or "Follow-up",
        "next_step": "Review and log the follow-up action.",
        "matched_opportunity_id": matched.get("opportunity_id") if matched else None,
    }


def _extract_with_llm(items: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    client = OpenAI(api_key=settings.openai_api_key)
    opportunity_context = [
        {
            "opportunity_id": opp.get("opportunity_id"),
            "client": opp.get("client"),
            "opportunity_name": opp.get("opportunity_name"),
            "bff_status": opp.get("bff_status"),
            "stage": opp.get("stage"),
            "industry_sector": opp.get("industry_sector"),
        }
        for opp in opportunities[:50]
    ]

    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({
                    "opportunities": opportunity_context,
                    "items": items,
                }, default=str),
            },
        ],
    )

    payload = json.loads(response.choices[0].message.content or "{}")
    return payload.get("entries", [])


def extract_log_entries(items: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return []
    if settings.openai_api_key:
        try:
            llm_entries = _extract_with_llm(items, opportunities)
            if llm_entries:
                return llm_entries
        except Exception:
            pass
    return [_fallback_extract(item, opportunities) for item in items]
