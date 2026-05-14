from typing import TYPE_CHECKING, Final, override

from sqlalchemy import Delete, Result, Select, delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.decks import decks_table

if TYPE_CHECKING:
    from collections.abc import Sequence


class AlchemyDeckGateway(DeckGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, deck: Deck) -> None:
        try:
            self._session.add(deck)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def delete_by_id(self, deck_id: DeckID) -> None:

        delete_stmt: Delete = delete(Deck).where(decks_table.c.id == deck_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, deck_id: DeckID) -> Deck | None:

        select_stmt: Select[tuple[Deck]] = select(Deck).where(decks_table.c.id == deck_id)

        try:
            rows: Result[tuple[Deck]] = await self._session.execute(select_stmt)
            deck: Deck | None = rows.scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return deck

    @override
    async def read_by_user_id(self, user_id: UserID) -> list[Deck]:

        select_stmt: Select[tuple[Deck]] = select(Deck).where(decks_table.c.owner_id == user_id)

        try:
            rows: Result[tuple[Deck]] = await self._session.execute(select_stmt)
            decks: Sequence[Deck] = rows.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

        return list(decks)

    @override
    async def read_public_decks(self, pagination: Pagination) -> list[Deck]:

        select_stmt: Select[tuple[Deck]] = select(Deck).offset(pagination.offset).limit(pagination.limit)

        try:
            rows: Result[tuple[Deck]] = await self._session.execute(select_stmt)
            decks: Sequence[Deck] = rows.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        else:
            return list(decks)

    @override
    async def count_by_user(self, user_id: UserID) -> int:

        select_stmt: Select[tuple[int]] = select(func.count(decks_table.c.id)).where(decks_table.c.owner_id == user_id)

        try:
            counter: Result[tuple[int]] = await self._session.execute(select_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        else:
            return counter.scalar_one()

    @override
    async def exists_with_deck_config_id(self, deck_config_id: DeckConfigID) -> bool:

        select_stmt: Select[tuple[bool]] = select(
            select(decks_table.c.id).where(decks_table.c.deck_config_id == deck_config_id).exists()
        )

        try:
            result: Result[tuple[bool]] = await self._session.execute(select_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        else:
            return result.scalar_one()
