from __future__ import annotations

from openai import OpenAI

from ..config import settings
from .service_catalog import catalog_has_any


def _lenai_available_by_catalog() -> bool:
    return catalog_has_any(["lenai", "openai"])


def has_llm_config() -> bool:
    if (
        settings.lenai_api_base_url
        and settings.lenai_api_key
        and settings.lenai_model
        and _lenai_available_by_catalog()
    ):
        return True
    if settings.openai_api_key and settings.openai_model:
        return True
    return False


def _build_openai_client() -> OpenAI:
    if settings.lenai_api_base_url and settings.lenai_api_key and _lenai_available_by_catalog():
        return OpenAI(
            api_key=settings.lenai_api_key,
            base_url=settings.lenai_api_base_url,
        )
    return OpenAI(api_key=settings.openai_api_key)


def _resolve_model() -> str:
    if settings.lenai_model and _lenai_available_by_catalog():
        return settings.lenai_model
    return settings.openai_model


def chat_json(system_prompt: str, user_payload: str) -> str:
    client = _build_openai_client()
    response = client.chat.completions.create(
        model=_resolve_model(),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload},
        ],
    )
    return response.choices[0].message.content or "{}"


def chat_text(prompt: str) -> str:
    client = _build_openai_client()
    response = client.chat.completions.create(
        model=_resolve_model(),
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""
