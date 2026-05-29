from datetime import timedelta
from typing import Literal, Any

from pydantic import BaseModel, Field, field_validator


class AuthSettings(BaseModel):
    jwt_secret: str = Field(
        alias="JWT_SECRET",
        description="JWT Secret Key.",
    )

    jwt_algorithm: Literal[
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ] = Field(alias="JWT_ALGORITHM")

    session_ttl_min: timedelta = Field(
        alias="SESSION_TTL_MIN",
        description="Session time to live in minutes.",
    )

    session_refresh_threshold: float = Field(
        alias="SESSION_REFRESH_THRESHOLD",
        description="Session refresh threshold.",
        gt=0.0,
        lt=1.0
    )

    @field_validator(session_ttl_min, mode="before")
    @classmethod
    def convert_session_ttl_min(cls, v: Any) -> timedelta:

        try:
            minutes = float(v)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"SESSION_TTl min must be a number, got string '{v}' that can not be converted to a number"
            ) from e


        if minutes < 1:
            raise ValueError("Time to live in minutes must be a positive number")

        return timedelta(minutes=minutes)

class CookieSettings:
    secure: bool = Field(
        alias="SECURE",
        description="Secure cookie.",
    )

class PasswordSettings:
    pepper: str = Field(
        alias="PEPPER",
        description="Pepper password.",
    )

class SecurityConfig(BaseModel):
    auth: AuthSettings
    cookies: CookieSettings
    password: PasswordSettings
