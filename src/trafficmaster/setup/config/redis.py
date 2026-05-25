from pydantic import BaseModel, Field


class RedisConfig(BaseModel):
    host: str = Field(
        alias="REDIS_HOST",
        description="Redis host",
    )

    port: int = Field(
        alias="REDIS_PORT",
        description="Redis port",
    )
