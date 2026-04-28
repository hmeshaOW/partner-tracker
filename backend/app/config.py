from pydantic import BaseModel
import os


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    lenai_api_base_url: str = os.getenv("LENAI_API_BASE_URL", "")
    lenai_api_key: str = os.getenv("LENAI_API_KEY", "")
    lenai_model: str = os.getenv("LENAI_MODEL", "")
    service_catalog_url: str = os.getenv(
        "SERVICE_CATALOG_URL",
        "https://mmcglobal.sharepoint.com/sites/EnterpriseArchitecture/SitePages/Core-APIs-and-Innovation(1).aspx",
    )
    service_catalog_bearer_token: str = os.getenv("SERVICE_CATALOG_BEARER_TOKEN", "")
    graph_base_url: str = "https://graph.microsoft.com/v1.0"
    opportunities_workbook_path: str = os.getenv(
        "OPPORTUNITIES_WORKBOOK_PATH",
        str(
            (
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                + "/documentation/Hany Opportunities Reporting.xlsx"
            )
        ),
    )
    bff_domains: list[str] = [
        "oliverwyman.com",
        "marshmclennan.com"
    ]


settings = Settings()
