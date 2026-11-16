import logging

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionHandler


async def test_unhandled_exception_is_logged_without_leaking_details(caplog: object) -> None:
    app = FastAPI()
    ExceptionHandler(app).setup_exception_handlers()

    @app.get("/boom")
    async def boom() -> None:
        msg = "sensitive internal details"
        raise RuntimeError(msg)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    with caplog.at_level(logging.ERROR, logger="trafficmaster.presentation.http.v1.common.exception_handler"):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"description": "Internal server error"}
    assert "method=GET path=/boom status_code=500" in caplog.text


async def test_gateway_error_hides_sql_and_server_paths(caplog: object) -> None:
    from trafficmaster.application.errors.gateway import GatewayError  # noqa: PLC0415

    # Arrange: an isolated application with an injected dependency failure.
    app = FastAPI()
    ExceptionHandler(app).setup_exception_handlers()

    @app.get("/unavailable")
    async def unavailable() -> None:
        msg = "SELECT secrets FROM users; /srv/private/config.py; asyncpg driver failure"
        raise GatewayError(msg)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    # Act.
    with caplog.at_level(logging.WARNING, logger="trafficmaster.presentation.http.v1.common.exception_handler"):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/unavailable")

    # Assert: details are available to server diagnostics and absent from the client response.
    assert response.status_code == 503
    assert response.json() == {"description": "Service temporary unavailable. Please try later."}
    assert "SELECT secrets" not in response.text
    assert "/srv/private" not in response.text
    assert "method=GET path=/unavailable status_code=503" in caplog.text
