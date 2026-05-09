from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID


class ReviewLogGateway(Protocol):
    @abstractmethod
    async def add(self, review: ReviewLog) -> None: ...

    @abstractmethod
    async def remove_by_id(self, review_id: ReviewLogID) -> None: ...

    @abstractmethod
    async def read_count_new_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
    ) -> int: ...

    @abstractmethod
    async def read_count_reviews_done(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        since: datetime,
    ) -> int: ...

    @abstractmethod
    async def read_by_card(
        self,
        user_id: UserID,
        card_id: CardID,
        pagination: Pagination,
    ) -> list[ReviewLog]: ...

    @abstractmethod
    async def read_by_user(
        self,
        user_id: UserID,
        deck_id: DeckID | None,
        pagination: Pagination,
    ) -> list[ReviewLog]: ...
