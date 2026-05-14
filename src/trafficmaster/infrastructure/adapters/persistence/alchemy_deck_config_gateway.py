from typing import TYPE_CHECKING, Final, override

from sqlalchemy import Delete, Result, Select, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.deck_configs import deck_configs_table

if TYPE_CHECKING:
    from collections.abc import Sequence


class AlchemyDeckConfigGateway(DeckConfigGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, deck_config: DeckConfig) -> None:
        try:
            self._session.add(deck_config)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def delete_by_id(self, deck_config_id: DeckConfigID) -> None:
        delete_stmt: Delete = delete(DeckConfig).where(deck_configs_table.c.id == deck_config_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, deck_config_id: DeckConfigID) -> DeckConfig | None:
        select_stmt: Select[tuple[DeckConfig]] = select(DeckConfig).where(deck_configs_table.c.id == deck_config_id)

        try:
            rows: Result[tuple[DeckConfig]] = await self._session.execute(select_stmt)
            deck_config: DeckConfig | None = rows.scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return deck_config

    @override
    async def read_by_user_id(self, user_id: UserID) -> list[DeckConfig]:
        select_stmt: Select[tuple[DeckConfig]] = select(DeckConfig).where(deck_configs_table.c.owner_id == user_id)

        try:
            rows: Result[tuple[DeckConfig]] = await self._session.execute(select_stmt)
            deck_configs: Sequence[DeckConfig] = rows.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return list(deck_configs)
