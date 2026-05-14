from typing import Any, Final

from pydantic import BaseModel, Field, field_validator, PostgresDsn
from consts import PORT_MAX, PORT_MIN


POOL_SIZE_MIN: Final[int] = 1
POOL_SIZE_MAX: Final[int] = 1000
POOL_RECYCLE_MIN: Final[int] = 1
POOL_OVERFLOW_MIN: Final[int] = 0

class PostgresConfig(BaseModel):

    user: str = Field(
        alias="POSTGRES_USER",
        description="Database user name",
    )

    password: str = Field(
        alias="POSTGRES_PASSWORD",
        description="Database password",
    )

    host: str = Field(
        alias="POSTGRES_HOST",
        description="Database host name",
        default="localhost",
    )

    port: int = Field(
        alias="POSTGRES_PORT",
        description="Database port",
    )

    db_name: str = Field(
        alias="POSTGRES_DB",
        description="Database name",
    )

    driver: str = Field(
        alias="POSTGRES_DRIVER",
        description="Database driver name",
    )

    @classmethod
    @field_validator("port")
    def validate_port(cls, v: int) -> int:
        if not PORT_MIN <= v <= PORT_MAX:
            raise ValueError(f"Port must be between {PORT_MIN} and {PORT_MAX}")
        return v

    @property
    def uri(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{self.driver}",
                username=self.user,
                password=self.password,
                port=self.port,
                host=self.host,
                path=self.db_name,
            )
        )

class SQLAlchemyConfig(BaseModel):

    pool_pre_ping: bool = Field(
        alias="DB_POOL_PRE_PING",
        description="Enable database pool pre ping.",
    )

    pool_size: int = Field(
        alias="DB_POOL_SIZE",
        description="Database connection pool size.",
    )

    pool_recycle: int = Field(
        alias="DB_POOL_RECYCLE",
        description="Database connection pool recycle.",
    )

    max_overflow: int = Field(
        alias="DB_POOL_MAX_OVERFLOW",
        description="Database connection pool max overflow.",
    )

    @classmethod
    @field_validator("pool_size")
    def validate_pool_size(cls, v: int) -> int:
        if not POOL_SIZE_MIN <= v <= POOL_SIZE_MAX:
            raise ValueError(
                f"DB_POOL_SIZE must be between {POOL_SIZE_MIN} and {POOL_SIZE_MAX}, got {v}."
            )
        return v

    @classmethod
    @field_validator("pool_recycle")
    def validate_pool_recycle(cls, v: int) -> int:
        if v < POOL_RECYCLE_MIN:
            raise ValueError(
                f"DB_POOL_RECYCLE must be at least {POOL_RECYCLE_MIN} minutes, got {v}."
            )
        return v

    @classmethod
    @field_validator("max_overflow")
    def validate_max_overflow(cls, v: int) -> int:
        if v < POOL_OVERFLOW_MIN:
            raise ValueError(
                f"DB_POOL_MAX_OVERFLOW must be at least {POOL_OVERFLOW_MIN}, got {v}."
            )
        return v

    echo: bool = Field(
        alias="DB_ECHO",
        description="Enable echo mode.",
        validate_default=False,
    )

    auto_flush: bool = Field(
        alias="DB_AUTO_FLUSH",
        description="Enable auto flush mode.",
        validate_default=False,
    )

    expire_on_commit: bool = Field(
        alias="DB_EXPIRE_ON_COMMIT",
        description="Expire ORM entities after commit. Keep False for async sessions.",
        default=False,
        validate_default=False,
    )
