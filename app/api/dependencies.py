"""Shared FastAPI dependencies."""

from app.config import Settings, get_settings


def settings_dependency() -> Settings:
    """Return application settings for request handlers."""

    return get_settings()
