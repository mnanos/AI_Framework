"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.config import get_settings
from app.observability.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure process-wide application concerns."""

    configure_logging()
    settings = get_settings()
    app.state.settings = settings
    get_logger(__name__).info(
        "application_starting",
        extra={"environment": settings.environment},
    )
    yield
    get_logger(__name__).info("application_stopping")


def create_app() -> FastAPI:
    """Create and configure the API application."""

    app = FastAPI(
        title="AI Framework",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    return app


app = create_app()
