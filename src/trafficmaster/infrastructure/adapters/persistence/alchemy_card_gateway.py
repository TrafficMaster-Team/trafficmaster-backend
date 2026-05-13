from typing import Final, override

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.cards import cards_table


class AlchemyCardGateway(CardGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, card: Card) -> None:
        try:
            self._session.add(card)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    async def delete_by_card_id(self, card_id: CardID) -> None:
        try:
            delete_stmt = delete(Card).where(cards_table.c.id == card_id)
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    async def delete_by_deck_id(self, deck_id: DeckID) -> None:
        try:
            delete_stmt = delete(Card).where(cards_table.c.id == deck_id)
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    async def read_by_id(self, card_id: CardID) -> Card | None:
        try:
            read_stmt = select(Card).where(cards_table.c.id == card_id)
            card: Card | None = (await self._session.execute(read_stmt)).scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return card

    async def read_all_by_deck_id(self, deck_id: DeckID) -> list[Card] | None:
        try:
            read_stmt = select(Card).where(cards_table.c.deck_id == deck_id)
            cards: list[Card] | None = (await self._session.execute(read_stmt)).scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return cards
