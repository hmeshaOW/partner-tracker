from __future__ import annotations

from datetime import datetime
from ..agents.domain_agent import classify_domain
from ..agents.relationship_agent import classify_relationship


def infer_from_messages(messages: list[dict]) -> list[dict]:
    inferred: list[dict] = []
    for msg in messages:
        sender = ((msg.get("from") or {}).get("emailAddress") or {}).get("address", "unknown@unknown")
        subject = msg.get("subject") or "(No Subject)"
        body_preview = msg.get("bodyPreview") or ""
        domain, confidence = classify_domain(f"{subject} {body_preview}")
        is_bff, is_external, org = classify_relationship(sender)
        inferred.append(
            {
                "id": msg.get("id", ""),
                "source": "email",
                "title": subject,
                "contact": sender,
                "organization": org,
                "domain": domain,
                "summary": body_preview[:220],
                "date": (msg.get("receivedDateTime") or datetime.utcnow().isoformat())[:10],
                "confidence": confidence,
                "is_bff": is_bff,
                "is_external": is_external,
            }
        )
    return inferred


def infer_from_events(events: list[dict]) -> list[dict]:
    inferred: list[dict] = []
    for event in events:
        organizer = ((event.get("organizer") or {}).get("emailAddress") or {}).get("address", "unknown@unknown")
        subject = event.get("subject") or "(No Title)"
        body_preview = event.get("bodyPreview") or ""
        domain, confidence = classify_domain(f"{subject} {body_preview}")
        is_bff, is_external, org = classify_relationship(organizer)
        start_time = ((event.get("start") or {}).get("dateTime") or datetime.utcnow().isoformat())
        inferred.append(
            {
                "id": event.get("id", ""),
                "source": "meeting",
                "title": subject,
                "contact": organizer,
                "organization": org,
                "domain": domain,
                "summary": body_preview[:220],
                "date": start_time[:10],
                "confidence": confidence,
                "is_bff": is_bff,
                "is_external": is_external,
            }
        )
    return inferred
