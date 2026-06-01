import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_index_returns_welcome(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello there! Welcome to FastAPI!"}
