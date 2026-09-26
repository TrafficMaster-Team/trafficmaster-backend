from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator


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

    trusted_hosts: list[str] = Field(
        alias="TRUSTED_HOSTS",
        description="Comma-separated Host header allowlist",
        default_factory=lambda: ["*"],
    )

    expose_api_docs: bool = Field(
        alias="EXPOSE_API_DOCS",
        description="Expose OpenAPI, Swagger UI, and ReDoc endpoints",
        default=True,
    )

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

    @field_validator("trusted_hosts", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [host.strip() for host in value.split(",") if host.strip()]
        return value

    @model_validator(mode="after")
    def reject_wildcard_origin_with_credentials(self) -> Self:
        if self.allow_credentials and "*" in self.allow_origins:
            msg = "CORS wildcard origin cannot be used when credentials are enabled"
            raise ValueError(msg)
        return self
