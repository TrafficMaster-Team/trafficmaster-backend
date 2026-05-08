from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID


class ReviewLogGateway(Protocol):
    @abstractmethod
    async def add(self, review: ReviewLog) -> None: ...

    @abstractmethod
    async def remove_by_id(self, review_id: ReviewLogID) -> None: ...
