from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID


class DeckGateway(Protocol):
    @abstractmethod
    async def add(self, deck: Deck) -> None: ...

    @abstractmethod
    async def delete_deck_by_id(self, deck_id: DeckID) -> None: ...

    @abstractmethod
    async def delete_deck_by_user_id(self, user_id: UserID) -> None: ...

    @abstractmethod
    async def read_deck_by_id(self, deck_id: DeckID) -> Deck | None: ...

    @abstractmethod
    async def read_decks_by_user_id(self, user_id: UserID) -> list[Deck] | None: ...
