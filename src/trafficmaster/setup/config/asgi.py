from pydantic import BaseModel, Field


class ASGIConfig(BaseModel):

    host: str = Field(
        alias="UVICORN_HOST",
        description="The host to listen on",
        default="0.0.0.0",
        validate_default=True,
    )

    port: int = Field(
        alias="UVICORN_PORT",
        description="The port to listen on",
        default=8000,
        validate_default=True,
    )

    fastapi_debug: bool = Field(
        alias="FASTAPI_DEBUG",
        default=True,
    )

    allow_credentials: bool = Field(
        alias="FASTAPI_ALLOW_CREDENTIALS",
        description="Allow access to FastAPI application",
        default=False,
    )

    allow_methods: list[str] = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]

    allow_headers: list[str] = [
        "Authorization",
        "Content-Type",
        "Cache-Control",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
    ]
