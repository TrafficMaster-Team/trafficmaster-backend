import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_liveness_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/healthcheck/live")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json() == {"status": "alive"}


async def test_readiness_returns_dependency_status(client: AsyncClient) -> None:
    response = await client.get("/healthcheck/ready")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json() == {"status": "ready", "database": "up", "cache": "up"}
