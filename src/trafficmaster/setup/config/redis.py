from typing import Final

from pydantic import BaseModel, Field, field_validator, RedisDsn

REDIS_MAX_CONNECTION_MIN: Final[int] = 1

class RedisConfig(BaseModel):
    host: str = Field(
        alias="REDIS_HOST",
        description="Redis host",
    )

    port: int = Field(
        alias="REDIS_PORT",
        description="Redis port",
    )

    max_connections: int = Field(
        alias="REDIS_MAX_CONNECTIONS",
        description="Redis max connections",
    )

    cache_db: int = Field(
        alias="REDIS_CACHE_DB",
        description="Redis cache db",
    )

    password: str = Field(
        alias="REDIS_PASSWORD",
        description="Redis password",
    )

    @field_validator("max_connections")
    @classmethod
    def validate_connections(cls, value: int) -> None:
        if value < REDIS_MAX_CONNECTION_MIN:
            raise ValueError(
                f"Redis max connections must be at least {REDIS_MAX_CONNECTION_MIN}",
            )

    @property
    def cache_uri(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.host,
                port=self.port,
                password=self.password,
                path=f"/{self.cache_db}"
            )
        )
