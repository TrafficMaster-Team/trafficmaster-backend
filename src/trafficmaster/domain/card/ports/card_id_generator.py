from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.card.values.card_id import CardID


class CardIdGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> CardID: ...
