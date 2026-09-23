from pydantic import BaseModel, Field, field_validator


class ASGIConfig(BaseModel):
    host: str = Field(
        alias="UVICORN_HOST",
        description="The host to listen on",
        default="0.0.0.0",  # noqa: S104
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
        default=False,
    )

    allow_credentials: bool = Field(
        alias="FASTAPI_ALLOW_CREDENTIALS",
        description="Allow credentials in cross-origin browser requests",
        default=False,
    )

    allow_origins: list[str] = Field(
        alias="CORS_ALLOWED_ORIGINS",
        description="Comma-separated frontend origins allowed to access the API",
        default_factory=list,
    )

    allow_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE"],
    )

    allow_headers: list[str] = Field(default_factory=lambda: ["Content-Type"])

    healthcheck_timeout_seconds: float = Field(
        alias="HEALTHCHECK_TIMEOUT_SECONDS",
        description="Maximum time to wait for each readiness dependency check",
        default=2.0,
        gt=0,
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_allow_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]

        return value
