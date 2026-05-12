"""Runtime configuration using environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and environment."""

    app_name: str = "Nistula Technical Assessment API"
    app_version: str = "1.0.0"
    environment: str = "development"

    anthropic_api_key: str = Field("", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_timeout_seconds: float = 15.0
    anthropic_max_tokens: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
