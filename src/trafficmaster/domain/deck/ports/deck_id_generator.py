from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.deck.values.deck_id import DeckID


class DeckIdGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> DeckID: ...
