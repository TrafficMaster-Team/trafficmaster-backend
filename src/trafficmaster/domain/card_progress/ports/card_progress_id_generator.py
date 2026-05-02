from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID


class CardProgressIdGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> CardProgressID: ...
