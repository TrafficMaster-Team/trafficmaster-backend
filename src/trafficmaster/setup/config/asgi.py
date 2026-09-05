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
        default=True,
    )

    allow_credentials: bool = Field(
        alias="FASTAPI_ALLOW_CREDENTIALS",
        description="Allow credentials in cross-origin browser requests",
        default=True,
    )

    allow_origins: list[str] = Field(
        alias="CORS_ALLOWED_ORIGINS",
        description="Comma-separated frontend origins allowed to access the API",
        default_factory=lambda: ["http://localhost:3000"],
        min_length=1,
    )

    allow_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE"],
    )

    allow_headers: list[str] = Field(default_factory=lambda: ["Content-Type"])

    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_allow_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]

        return value
