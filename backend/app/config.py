from pydantic import BaseModel
import os


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    graph_base_url: str = "https://graph.microsoft.com/v1.0"
    bff_domains: list[str] = [
        "oliverwyman.com",
        "marshmclennan.com"
    ]


settings = Settings()
