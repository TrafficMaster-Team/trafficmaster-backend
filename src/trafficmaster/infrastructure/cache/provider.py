from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from trafficmaster.setup.config.redis import RedisConfig


async def get_redis_pool(redis_config: RedisConfig) -> ConnectionPool:
    return ConnectionPool.from_url(
        url=redis_config.cache_uri, max_connections=redis_config.max_connections, decode_responses=False
    )


async def get_redis(connection_pool: ConnectionPool) -> AsyncGenerator[Redis, None]:
    client: Redis = Redis.from_pool(connection_pool)
    try:
        yield client
    finally:
        await client.aclose()
