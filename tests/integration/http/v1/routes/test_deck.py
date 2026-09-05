import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_public_decks_allow_shared_cache(client: AsyncClient) -> None:
    response = await client.get("/v1/deck/public")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Cache-Control"] == "public, max-age=60"
