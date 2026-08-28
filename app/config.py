"""Validated application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or `.env`."""

    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"),
    )
    openai_api_key: SecretStr | None = None
    database_url: str = "postgresql+asyncpg://ai:ai@localhost:5432/ai"
    redis_url: str = "redis://localhost:6379/0"
    langfuse_public_key: str | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_base_url: str | None = None
    artifact_root: Path = Path("./data/artifacts")
    sandbox_enabled: bool = True
    sandbox_image: str = "ai-framework-sandbox:latest"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
