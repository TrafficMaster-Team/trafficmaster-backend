import os

from pydantic import BaseModel, Field

from trafficmaster.setup.config.asgi import ASGIConfig
from trafficmaster.setup.config.database import PostgresConfig, SQLAlchemyConfig
from trafficmaster.setup.config.redis import RedisConfig
from trafficmaster.setup.config.security import SecurityConfig


class AppConfig(BaseModel):

    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**os.environ),
        description="postgres settings"
    )

    sqlalchemy: SQLAlchemyConfig = Field(
        default_factory=lambda: SQLAlchemyConfig(**os.environ),
        description="sqlalchemy settings"
    )

    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig(**os.environ),
        description="redis settings"
    )

    asgi: ASGIConfig = Field(
        default_factory= lambda: ASGIConfig(**os.environ),
        description="asgi settings"
    )

    security: SecurityConfig = Field(
        default_factory= lambda: SecurityConfig(**os.environ),
        description="security settings"
    )
