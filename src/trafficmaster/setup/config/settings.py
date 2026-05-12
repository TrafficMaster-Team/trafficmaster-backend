import os

from pydantic import BaseModel, Field

from trafficmaster.setup.config.database import PostgresConfig, SQLAlchemyConfig


class AppConfig(BaseModel):

    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**os.environ),
        description="postgres settings"
    )

    sqlalchemy: SQLAlchemyConfig = Field(
        default_factory=lambda: SQLAlchemyConfig(**os.environ),
        description="sqlalchemy settings"
    )
