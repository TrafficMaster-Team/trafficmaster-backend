import uuid

import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_signup_login_me_logout_flow(client: AsyncClient) -> None:
    email = f"tester_{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecure123"  # noqa: S105
    name = "Integration-Tester"

    # Sign up
    signup = await client.post(
        "/v1/auth/signup",
        json={"email": email, "name": name, "password": password},
    )
    assert signup.status_code == status.HTTP_201_CREATED
    created_id = signup.json()["id"]

    # Log in (sets the auth cookie on the client)
    login = await client.post(
        "/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == status.HTTP_204_NO_CONTENT

    # Read the current user using the session cookie
    me = await client.get("/v1/auth/me")
    assert me.status_code == status.HTTP_200_OK
    body = me.json()
    assert body["id"] == created_id
    assert body["email"] == email
    assert body["name"] == name

    # Log out
    logout = await client.post("/v1/auth/logout")
    assert logout.status_code == status.HTTP_204_NO_CONTENT


async def test_login_with_unknown_email_fails(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/auth/login",
        json={"email": f"missing_{uuid.uuid4().hex[:8]}@example.com", "password": "SuperSecure123"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_signup_rejects_duplicate_email(client: AsyncClient) -> None:
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecure123"  # noqa: S105
    payload = {"email": email, "name": "Dup-Tester", "password": password}

    first = await client.post("/v1/auth/signup", json=payload)
    assert first.status_code == status.HTTP_201_CREATED

    # logout so the second signup is not blocked by an active session
    await client.post("/v1/auth/logout")

    second = await client.post("/v1/auth/signup", json=payload)
    assert second.status_code == status.HTTP_409_CONFLICT
