from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID


class DeckConfigIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> DeckConfigID: ...
