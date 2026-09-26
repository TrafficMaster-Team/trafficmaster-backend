import os
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from trafficmaster.setup.config.asgi import ASGIConfig
from trafficmaster.setup.config.database import PostgresConfig, SQLAlchemyConfig
from trafficmaster.setup.config.redis import RedisConfig
from trafficmaster.setup.config.security import AuthSettings, CookieSettings, PasswordSettings, SecurityConfig

AppEnvironment = Literal["development", "test", "production"]

_MIN_SECRET_LENGTH = 32
_PLACEHOLDER_SECRETS = {
    "REPLACE_THIS_WITH_YOUR_OWN_SECRET_VALUE",
    "REPLACE_THIS_WITH_YOUR_OWN_SECRET_PEPPER_VALUE",
}


class AppConfig(BaseModel):
    environment: AppEnvironment = Field(default="development", alias="APP_ENV")

    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**os.environ),
        description="postgres settings",
    )

    sqlalchemy: SQLAlchemyConfig = Field(
        default_factory=lambda: SQLAlchemyConfig(**os.environ),
        description="sqlalchemy settings",
    )

    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig(**os.environ),
        description="redis settings",
    )

    asgi: ASGIConfig = Field(
        default_factory=lambda: ASGIConfig(**os.environ),
        description="asgi settings",
    )

    security: SecurityConfig = Field(
        default_factory=lambda: SecurityConfig(
            auth=AuthSettings(**os.environ),
            cookies=CookieSettings(**os.environ),
            password=PasswordSettings(**os.environ),
        ),
        description="security settings",
    )

    @model_validator(mode="after")
    def validate_production_safety(self) -> Self:
        if self.environment != "production":
            return self

        unsafe_settings: list[str] = []
        if self.asgi.fastapi_debug:
            unsafe_settings.append("FASTAPI_DEBUG must be false")
        if not self.security.cookies.secure:
            unsafe_settings.append("SECURE must be true")
        if not self._is_strong_secret(self.security.auth.jwt_secret):
            unsafe_settings.append(f"JWT_SECRET must contain at least {_MIN_SECRET_LENGTH} characters")
        if not self._is_strong_secret(self.security.password.pepper):
            unsafe_settings.append(f"PEPPER must contain at least {_MIN_SECRET_LENGTH} characters")
        if any(origin == "*" or not origin.startswith("https://") for origin in self.asgi.allow_origins):
            unsafe_settings.append("CORS_ALLOWED_ORIGINS must contain only explicit HTTPS origins")
        if not self.asgi.trusted_hosts or "*" in self.asgi.trusted_hosts:
            unsafe_settings.append("TRUSTED_HOSTS must contain an explicit host allowlist")

        if unsafe_settings:
            msg = "Unsafe production configuration: " + "; ".join(unsafe_settings)
            raise ValueError(msg)
        return self

    @staticmethod
    def _is_strong_secret(value: str) -> bool:
        return len(value) >= _MIN_SECRET_LENGTH and value not in _PLACEHOLDER_SECRETS
