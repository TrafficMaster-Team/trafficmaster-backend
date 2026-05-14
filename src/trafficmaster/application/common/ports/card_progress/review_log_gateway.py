from datetime import datetime
from typing import Protocol

from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID


class ReviewLogGateway(Protocol):
    async def add(self, review: ReviewLog) -> None: ...

    async def delete_by_id(self, review_id: ReviewLogID) -> None: ...

    async def count_new_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
    ) -> int: ...

    async def count_reviews_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
    ) -> int: ...

    async def read_by_card(
        self,
        user_id: UserID,
        card_id: CardID,
        pagination: Pagination,
    ) -> list[ReviewLog]: ...

    async def read_by_user(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        pagination: Pagination,
    ) -> list[ReviewLog]: ...
