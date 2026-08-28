from app.api.routes.health import health, ready
from app.config import Settings
from app.main import create_app


async def test_health_endpoint() -> None:
    response = await health(Settings())

    assert response.model_dump() == {
        "status": "ok",
        "service": "ai-framework",
        "environment": "development",
    }


async def test_ready_endpoint() -> None:
    response = await ready(Settings())

    assert response.status == "ok"


def test_app_registers_health_routes() -> None:
    paths = {route.path for route in create_app().routes}

    assert "/health" in paths
    assert "/ready" in paths
