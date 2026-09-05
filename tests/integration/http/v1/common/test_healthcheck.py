import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_healthcheck_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/healthcheck/")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json() == {"message": "OK", "status": "success"}
