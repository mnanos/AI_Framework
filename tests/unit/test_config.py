from pathlib import Path

from app.config import Settings


def test_settings_load_environment_alias(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    settings = Settings()

    assert settings.environment == "test"


def test_settings_defaults_are_local_development_safe() -> None:
    settings = Settings()

    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert settings.redis_url.startswith("redis://")
    assert settings.artifact_root == Path("./data/artifacts")
