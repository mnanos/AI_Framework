"""Health and readiness endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import settings_dependency
from app.config import Settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Basic service health response."""

    status: str
    service: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health(settings: Annotated[Settings, Depends(settings_dependency)]) -> HealthResponse:
    """Return process health."""

    return HealthResponse(
        status="ok",
        service="ai-framework",
        environment=settings.environment,
    )


@router.get("/ready", response_model=HealthResponse)
async def ready(settings: Annotated[Settings, Depends(settings_dependency)]) -> HealthResponse:
    """Return readiness for dependencies introduced in later milestones."""

    return HealthResponse(
        status="ok",
        service="ai-framework",
        environment=settings.environment,
    )
