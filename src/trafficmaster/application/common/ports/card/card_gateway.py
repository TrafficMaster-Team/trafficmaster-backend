from abc import abstractmethod
from typing import Protocol

from trafficmaster.application.common.query_params.card_filters import CardParams
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.deck.values.deck_id import DeckID


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
