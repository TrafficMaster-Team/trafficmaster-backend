from datetime import datetime
from typing import TYPE_CHECKING, Final, override

from sqlalchemy import Result, Select, delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.infrastructure.adapters.persistence.constants import DB_QUERY_FAILED
from trafficmaster.infrastructure.persistence.models.cards import cards_table
from trafficmaster.infrastructure.persistence.models.review_logs import review_logs_table

if TYPE_CHECKING:
    from collections.abc import Sequence


class AlchemyReviewLogGateway(ReviewLogGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, review: ReviewLog) -> None:
        self._session.add(review)

    @override
    async def delete_by_id(self, review_id: ReviewLogID) -> None:
        delete_stmt = delete(ReviewLog).where(review_logs_table.c.id == review_id)

        try:
            await self._session.execute(delete_stmt)
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error

    @override
    async def count_new_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
    ) -> int:
        return await self._count_done(user_id, deck_id, since, is_new=True)

    @override
    async def count_reviews_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
    ) -> int:
        return await self._count_done(user_id, deck_id, since, is_new=False)

    @override
    async def read_by_card(
        self,
        user_id: UserID,
        card_id: CardID,
        pagination: Pagination,
    ) -> list[ReviewLog]:
        select_stmt: Select[tuple[ReviewLog]] = (
            select(ReviewLog)
            .where(
                review_logs_table.c.user_id == user_id,
                review_logs_table.c.card_id == card_id,
            )
            .order_by(review_logs_table.c.reviewed_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        try:
            rows: Result[tuple[ReviewLog]] = await self._session.execute(select_stmt)
            logs: Sequence[ReviewLog] = rows.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return list(logs)

    @override
    async def read_by_user(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        pagination: Pagination,
    ) -> list[ReviewLog]:
        select_stmt: Select[tuple[ReviewLog]] = select(ReviewLog).where(
            review_logs_table.c.user_id == user_id,
        )

        if deck_id is not None:
            select_stmt = select_stmt.select_from(
                review_logs_table.join(cards_table, review_logs_table.c.card_id == cards_table.c.id),
            ).where(cards_table.c.deck_id == deck_id)

        select_stmt = (
            select_stmt.order_by(review_logs_table.c.reviewed_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        try:
            rows: Result[tuple[ReviewLog]] = await self._session.execute(select_stmt)
            logs: Sequence[ReviewLog] = rows.scalars().all()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return list(logs)

    async def _count_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
        *,
        is_new: bool,
    ) -> int:
        state_filter = (
            review_logs_table.c.card_state == CardState.NEW
            if is_new
            else review_logs_table.c.card_state != CardState.NEW
        )

        select_stmt: Select[tuple[int]] = select(func.count(review_logs_table.c.id)).where(
            review_logs_table.c.user_id == user_id,
            review_logs_table.c.reviewed_at >= since,
            state_filter,
        )

        if deck_id is not None:
            select_stmt = select_stmt.select_from(
                review_logs_table.join(cards_table, review_logs_table.c.card_id == cards_table.c.id),
            ).where(cards_table.c.deck_id == deck_id)

        try:
            result: Result[tuple[int]] = await self._session.execute(select_stmt)
            count: int = result.scalar_one()
        except SQLAlchemyError as error:
            raise GatewayError(DB_QUERY_FAILED) from error
        return count
