from typing import TYPE_CHECKING, Final, override

from sqlalchemy import ColumnElement, Result, Select, delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.query_params.card_filters import CardParams
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.cards import cards_table
from trafficmaster.infrastructure.persistence.models.decks import decks_table

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID


class AlchemyCardGateway(CardGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, card: Card) -> None:
        try:
            self._session.add(card)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def delete_by_card_id(self, card_id: CardID) -> None:
        try:
            delete_stmt = delete(Card).where(cards_table.c.id == card_id)
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def delete_by_deck_id(self, deck_id: DeckID) -> None:
        try:
            delete_stmt = delete(Card).where(cards_table.c.deck_id == deck_id)
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, card_id: CardID) -> Card | None:
        try:
            read_stmt = select(Card).where(cards_table.c.id == card_id)
            card: Card | None = (await self._session.execute(read_stmt)).scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return card

    @override
    async def read_all_by_deck(self, deck_id: DeckID) -> list[Card]:
        try:
            read_stmt = select(Card).where(cards_table.c.deck_id == deck_id)
            cards: Sequence[Card] = (await self._session.execute(read_stmt)).scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return list(cards)

    @override
    async def read_all_deck_cards(self, deck_id: DeckID, card_params: CardParams) -> list[Card] | None:
        table_sorting_field: ColumnElement[UUID | str] | None = cards_table.c.get(card_params.sorting_filter)

        if table_sorting_field is None:
            return None

        order_by_param: ColumnElement[UUID | str] = (
            table_sorting_field.asc() if card_params.sorting_order == SortingOrder.ASC else table_sorting_field.desc()
        )

        select_stmt: Select[tuple[Card]] = (
            select(Card)
            .where(cards_table.c.deck_id == deck_id)
            .order_by(order_by_param)
            .limit(card_params.pagination.limit)
            .offset(card_params.pagination.offset)
        )

        try:
            cards: Result[tuple[Card]] = await self._session.execute(select_stmt)
            rows: Sequence[Card] = cards.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        else:
            return list(rows)

    @override
    async def count_by_deck(self, deck_id: DeckID) -> int:
        select_stmt = select(func.count(cards_table.c.id)).where(cards_table.c.deck_id == deck_id)

        try:
            result: Result[tuple[int]] = await self._session.execute(select_stmt)
            count: int = result.scalar_one()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        else:
            return count

    @override
    async def count_by_user(self, user_id: UserID) -> int:
        select_stmt = (
            select(func.count(cards_table.c.id))
            .select_from(cards_table.join(decks_table, cards_table.c.deck_id == decks_table.c.id))
            .where(decks_table.c.owner_id == user_id)
        )

        try:
            result: Result[tuple[int]] = await self._session.execute(select_stmt)
            count: int = result.scalar_one()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        else:
            return count
