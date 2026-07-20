"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.4-mini"
    azure_openai_api_version: str = "2024-12-01-preview"
    model_name: str = "gpt-5.4-mini"
    request_timeout: float = 30.0

    model_config = {"env_file": str(_ENV_FILE) if _ENV_FILE.exists() else None, "extra": "ignore"}


settings = Settings()
