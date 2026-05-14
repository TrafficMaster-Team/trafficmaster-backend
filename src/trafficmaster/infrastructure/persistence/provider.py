from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from trafficmaster.setup.config.database import PostgresConfig, SQLAlchemyConfig


async def get_engine(
    postgres_config: PostgresConfig,
    sqlalchemy_config: SQLAlchemyConfig,
) -> AsyncIterator[AsyncEngine]:
    engine: AsyncEngine = create_async_engine(
        postgres_config.uri,
        echo=sqlalchemy_config.echo,
        pool_pre_ping=sqlalchemy_config.pool_pre_ping,
        pool_size=sqlalchemy_config.pool_size,
        pool_recycle=sqlalchemy_config.pool_recycle,
        max_overflow=sqlalchemy_config.max_overflow,
    )

    yield engine
    await engine.dispose()


def get_sessionmaker(
    engine: AsyncEngine,
    sqlalchemy_config: SQLAlchemyConfig,
) -> async_sessionmaker[AsyncSession]:

    return async_sessionmaker(
        bind=engine,
        expire_on_commit=sqlalchemy_config.expire_on_commit,
        autoflush=sqlalchemy_config.auto_flush,
    )


async def get_session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    async with sessionmaker() as session:
        yield session
