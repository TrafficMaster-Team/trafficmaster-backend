from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.user.values.user_id import UserID


class DeckConfigGateway(Protocol):
    @abstractmethod
    async def add(self, deck_config: DeckConfig) -> None: ...

    @abstractmethod
    async def delete_by_id(self, deck_config_id: DeckConfigID) -> None: ...

    @abstractmethod
    async def read_by_id(self, deck_config_id: DeckConfigID) -> DeckConfig | None: ...

    @abstractmethod
    async def read_by_user_id(self, user_id: UserID) -> list[DeckConfig] | None: ...
