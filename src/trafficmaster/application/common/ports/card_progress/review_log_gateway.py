from abc import abstractmethod
from datetime import datetime
from typing import Protocol

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
        deck_id: DeckID,
        since: datetime,
    ) -> int: ...

    @abstractmethod
    async def read_count_reviews_done(
        self,
        user_id: UserID,
        deck_id: DeckID,
        since: datetime,
    ) -> int: ...
