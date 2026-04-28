from __future__ import annotations

from datetime import datetime
from ..agents.log_entry_agent import extract_log_entries


def _normalize_message(message: dict) -> dict:
    sender = ((message.get("from") or {}).get("emailAddress") or {}).get("address", "unknown@unknown")
    recipients = [
        (recipient.get("emailAddress") or {}).get("address", "")
        for recipient in (message.get("toRecipients") or [])
    ]
    cc_recipients = [
        (recipient.get("emailAddress") or {}).get("address", "")
        for recipient in (message.get("ccRecipients") or [])
    ]
    body = ((message.get("body") or {}).get("content") or message.get("bodyPreview") or "")
    return {
        "id": message.get("id", ""),
        "source": "email",
        "title": message.get("subject") or "(No Subject)",
        "contact": sender,
        "body_preview": body,
        "date": (message.get("receivedDateTime") or datetime.utcnow().isoformat())[:10],
        "participants": [sender, *recipients, *cc_recipients],
    }


def _normalize_event(event: dict) -> dict:
    organizer = ((event.get("organizer") or {}).get("emailAddress") or {}).get("address", "unknown@unknown")
    attendees = [
        ((attendee.get("emailAddress") or {}).get("address") or "")
        for attendee in (event.get("attendees") or [])
    ]
    body = ((event.get("body") or {}).get("content") or event.get("bodyPreview") or "")
    start_time = ((event.get("start") or {}).get("dateTime") or datetime.utcnow().isoformat())
    return {
        "id": event.get("id", ""),
        "source": "meeting",
        "title": event.get("subject") or "(No Title)",
        "contact": organizer,
        "body_preview": body,
        "date": start_time[:10],
        "participants": [organizer, *attendees],
    }


def infer_from_messages(messages: list[dict], opportunities: list[dict]) -> list[dict]:
    normalized = []
    for msg in messages:
        normalized.append(_normalize_message(msg))
    return [
        {
            "id": entry.get("source_id") or entry.get("id") or "",
            **entry,
        }
        for entry in extract_log_entries(normalized, opportunities)
    ]


def infer_from_events(events: list[dict], opportunities: list[dict]) -> list[dict]:
    normalized = []
    for event in events:
        normalized.append(_normalize_event(event))
    return [
        {
            "id": entry.get("source_id") or entry.get("id") or "",
            **entry,
        }
        for entry in extract_log_entries(normalized, opportunities)
    ]
