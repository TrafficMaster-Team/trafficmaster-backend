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
