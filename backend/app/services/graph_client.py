from __future__ import annotations

import httpx
from . import storage
from ..config import settings
from .service_catalog import resolve_graph_base_url


class GraphClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.graph_base_url = resolve_graph_base_url(settings.graph_base_url)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def fetch_messages(self, limit: int = 50) -> list[dict]:
        url = (
            f"{self.graph_base_url}/me/messages"
            f"?$top={limit}&$select=id,subject,bodyPreview,body,receivedDateTime,from,toRecipients,ccRecipients,conversationId"
        )
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("value", [])

    async def fetch_events(self, limit: int = 30) -> list[dict]:
        url = (
            f"{self.graph_base_url}/me/events"
            f"?$top={limit}&$select=id,subject,bodyPreview,body,start,end,organizer,attendees,location,onlineMeetingUrl"
        )
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("value", [])


def save_inferred(activities: list[dict]) -> None:
    storage.write_activities(activities)
