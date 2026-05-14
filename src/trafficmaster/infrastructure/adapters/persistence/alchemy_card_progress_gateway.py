from datetime import datetime
from typing import TYPE_CHECKING, Final, override

from sqlalchemy import Result, Select, and_, delete, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.card_with_progress import CardWithProgress
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.card_progress import card_progress_table
from trafficmaster.infrastructure.persistence.models.cards import cards_table
from trafficmaster.infrastructure.persistence.models.decks import decks_table

if TYPE_CHECKING:
    from collections.abc import Sequence

_LEARNING_STATES: Final = (CardState.LEARNING, CardState.RELEARNING)


class AlchemyCardProgressGateway(CardProgressGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, progress: CardProgress) -> None:
        try:
            self._session.add(progress)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def delete_by_id(self, progress_id: CardProgressID) -> None:
        delete_stmt = delete(CardProgress).where(card_progress_table.c.id == progress_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, progress_id: CardProgressID) -> CardProgress | None:
        select_stmt: Select[tuple[CardProgress]] = select(CardProgress).where(
            card_progress_table.c.id == progress_id,
        )

        try:
            rows: Result[tuple[CardProgress]] = await self._session.execute(select_stmt)
            progress: CardProgress | None = rows.scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return progress

    @override
    async def read_by_user_and_card(
        self,
        user_id: UserID,
        card_id: CardID,
    ) -> CardProgress | None:
        select_stmt: Select[tuple[CardProgress]] = select(CardProgress).where(
            card_progress_table.c.user_id == user_id,
            card_progress_table.c.card_id == card_id,
        )

        try:
            rows: Result[tuple[CardProgress]] = await self._session.execute(select_stmt)
            progress: CardProgress | None = rows.scalar_one_or_none()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return progress

    @override
    async def read_due_learning(
        self,
        user_id: UserID,
        deck_id: DeckID,
        now: datetime,
        limit: int,
    ) -> list[CardWithProgress]:
        select_stmt: Select[tuple[Card, CardProgress]] = (
            select(Card, CardProgress)
            .join(CardProgress, card_progress_table.c.card_id == cards_table.c.id)
            .where(
                cards_table.c.deck_id == deck_id,
                card_progress_table.c.user_id == user_id,
                card_progress_table.c.state.in_(_LEARNING_STATES),
                card_progress_table.c.next_review_at <= now,
            )
            .order_by(card_progress_table.c.next_review_at)
            .limit(limit)
        )

        return await self._fetch_cards_with_progress(select_stmt)

    @override
    async def read_due_review(
        self,
        user_id: UserID,
        deck_id: DeckID,
        now: datetime,
        limit: int,
    ) -> list[CardWithProgress]:
        select_stmt: Select[tuple[Card, CardProgress]] = (
            select(Card, CardProgress)
            .join(CardProgress, card_progress_table.c.card_id == cards_table.c.id)
            .where(
                cards_table.c.deck_id == deck_id,
                card_progress_table.c.user_id == user_id,
                card_progress_table.c.state == CardState.REVIEW,
                card_progress_table.c.next_review_at <= now,
            )
            .order_by(card_progress_table.c.next_review_at)
            .limit(limit)
        )

        return await self._fetch_cards_with_progress(select_stmt)

    @override
    async def read_new_cards(
        self,
        user_id: UserID,
        deck_id: DeckID,
        now: datetime,
        limit: int,
        order: NewCardOrder,
    ) -> list[CardWithProgress]:
        progress_join = cards_table.outerjoin(
            card_progress_table,
            and_(
                card_progress_table.c.card_id == cards_table.c.id,
                card_progress_table.c.user_id == user_id,
            ),
        )
        order_by = func.random() if order == NewCardOrder.RANDOM else cards_table.c.created_at

        select_stmt: Select[tuple[Card, CardProgress]] = (
            select(Card, CardProgress)
            .select_from(progress_join)
            .where(
                cards_table.c.deck_id == deck_id,
                or_(
                    card_progress_table.c.id.is_(None),
                    card_progress_table.c.state == CardState.NEW,
                ),
            )
            .order_by(order_by)
            .limit(limit)
        )

        return await self._fetch_cards_with_progress(select_stmt)

    @override
    async def count_by_state(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
    ) -> dict[CardState | None, int]:
        progress_join = cards_table.outerjoin(
            card_progress_table,
            and_(
                card_progress_table.c.card_id == cards_table.c.id,
                card_progress_table.c.user_id == user_id,
            ),
        )

        select_stmt: Select[tuple[CardState | None, int]] = select(
            card_progress_table.c.state,
            func.count(cards_table.c.id),
        ).group_by(card_progress_table.c.state)

        if deck_id is not None:
            select_stmt = select_stmt.select_from(progress_join).where(cards_table.c.deck_id == deck_id)
        else:
            select_stmt = select_stmt.select_from(
                progress_join.join(decks_table, decks_table.c.id == cards_table.c.deck_id),
            ).where(decks_table.c.owner_id == user_id)

        try:
            rows: Result[tuple[CardState | None, int]] = await self._session.execute(select_stmt)
            counts: Sequence[tuple[CardState | None, int]] = rows.tuples().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return dict(counts)

    @override
    async def count_due_learning(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        now: datetime,
    ) -> int:
        return await self._count_due(user_id, deck_id, now, states=_LEARNING_STATES)

    @override
    async def count_due_review(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        now: datetime,
    ) -> int:
        return await self._count_due(user_id, deck_id, now, states=(CardState.REVIEW,))

    async def _count_due(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        now: datetime,
        *,
        states: tuple[CardState, ...],
    ) -> int:
        select_stmt: Select[tuple[int]] = select(func.count(card_progress_table.c.id)).where(
            card_progress_table.c.user_id == user_id,
            card_progress_table.c.state.in_(states),
            card_progress_table.c.next_review_at <= now,
        )

        if deck_id is not None:
            select_stmt = select_stmt.select_from(
                card_progress_table.join(cards_table, cards_table.c.id == card_progress_table.c.card_id),
            ).where(cards_table.c.deck_id == deck_id)

        try:
            result: Result[tuple[int]] = await self._session.execute(select_stmt)
            count: int = result.scalar_one()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return count

    async def _fetch_cards_with_progress(
        self,
        select_stmt: Select[tuple[Card, CardProgress]],
    ) -> list[CardWithProgress]:
        try:
            rows: Result[tuple[Card, CardProgress]] = await self._session.execute(select_stmt)
            pairs: Sequence[tuple[Card, CardProgress]] = rows.tuples().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return [CardWithProgress(card=card, progress=progress) for card, progress in pairs]
