from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID


class ReviewIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> ReviewLogID: ...
