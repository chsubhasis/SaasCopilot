import sys
from typing import List

from pydantic import AnyHttpUrl  # type: ignore
from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # Meta

    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    # e.g: http://localhost,http://localhost:4200,http://localhost:3000
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # type: ignore
        "http://localhost:8000",  # type: ignore
        "https://localhost:3000",  # type: ignore
        "https://localhost:8000",  # type: ignore
    ]

    PROJECT_NAME: str = "SaaS Copilot"

    class Config:
        case_sensitive = True


settings = Settings()
