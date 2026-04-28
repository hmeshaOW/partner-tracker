from __future__ import annotations

import re
import time
from urllib.parse import urljoin

import httpx

from ..config import settings


_CACHE_TTL_SECONDS = 300
_cached_entries: list[dict[str, str]] = []
_cached_at = 0.0


def _build_headers() -> dict[str, str]:
    headers = {"Accept": "text/html,application/json"}
    if settings.service_catalog_bearer_token:
        headers["Authorization"] = f"Bearer {settings.service_catalog_bearer_token}"
    return headers


def _extract_entries_from_html(html: str, base_url: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for href, label in re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', html, flags=re.IGNORECASE):
        name = re.sub(r"\s+", " ", label).strip()
        if not name:
            continue
        entries.append(
            {
                "name": name,
                "url": urljoin(base_url, href),
            }
        )

    page_text = re.sub(r"<[^>]+>", " ", html)
    for keyword in ("LenAI", "OpenAI", "Graph", "Innovation", "Core APIs"):
        if keyword.lower() in page_text.lower() and all(entry["name"].lower() != keyword.lower() for entry in entries):
            entries.append({"name": keyword, "url": base_url})

    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in entries:
        unique[(item["name"], item["url"])] = item
    return list(unique.values())


def _fetch_catalog_entries() -> list[dict[str, str]]:
    if not settings.service_catalog_url:
        return []
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(settings.service_catalog_url, headers=_build_headers())
            response.raise_for_status()
            content_type = (response.headers.get("content-type") or "").lower()
            if "application/json" in content_type:
                data = response.json()
                if isinstance(data, list):
                    return [
                        {
                            "name": str(item.get("name") or item.get("title") or ""),
                            "url": str(item.get("url") or item.get("endpoint") or settings.service_catalog_url),
                        }
                        for item in data
                        if isinstance(item, dict)
                    ]
                return []
            return _extract_entries_from_html(response.text, settings.service_catalog_url)
    except Exception:
        return []


def get_catalog_services(force_refresh: bool = False) -> list[dict[str, str]]:
    global _cached_at, _cached_entries
    now = time.time()
    if not force_refresh and _cached_entries and now - _cached_at < _CACHE_TTL_SECONDS:
        return _cached_entries

    _cached_entries = _fetch_catalog_entries()
    _cached_at = now
    return _cached_entries


def catalog_has_any(needles: list[str]) -> bool:
    services = get_catalog_services()
    if not services:
        return False

    lowered_needles = [needle.lower() for needle in needles]
    for service in services:
        text = f"{service.get('name', '')} {service.get('url', '')}".lower()
        if any(needle in text for needle in lowered_needles):
            return True
    return False


def resolve_graph_base_url(default_url: str) -> str:
    services = get_catalog_services()
    for service in services:
        url = service.get("url", "")
        text = f"{service.get('name', '')} {url}".lower()
        if "graph" in text and "graph.microsoft.com" in url:
            return url.rstrip("/")
    return default_url
