from __future__ import annotations

from ..config import settings


def parse_org(email: str) -> str:
    if "@" not in email:
        return "unknown"
    domain = email.split("@", 1)[1].lower()
    return domain


def classify_relationship(email: str) -> tuple[bool, bool, str]:
    domain = parse_org(email)
    is_bff = domain in settings.bff_domains
    is_external = not is_bff
    return is_bff, is_external, domain
