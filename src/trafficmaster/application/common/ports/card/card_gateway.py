from abc import abstractmethod
from typing import Protocol

from trafficmaster.application.common.query_params.card_filters import CardParams
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.values.user_id import UserID


class CardGateway(Protocol):
    @abstractmethod
    async def add(self, card: Card) -> None: ...

    @abstractmethod
    async def delete_by_card_id(self, card_id: CardID) -> None: ...

    @abstractmethod
    async def delete_by_deck_id(self, deck_id: DeckID) -> None: ...

    @abstractmethod
    async def read_by_id(self, card_id: CardID) -> Card | None: ...

    @abstractmethod
    async def read_all_deck_cards(self, deck_id: DeckID, card_params: CardParams) -> list[Card] | None: ...

    @abstractmethod
    async def count_by_deck(self, deck_id: DeckID) -> int: ...

    @abstractmethod
    async def read_all_by_deck(self, deck_id: DeckID) -> list[Card]: ...

    @abstractmethod
    async def count_by_user(self, user_id: UserID) -> int: ...
