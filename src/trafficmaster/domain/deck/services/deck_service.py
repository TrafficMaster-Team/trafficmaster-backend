from typing import Final

from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.ports.deck_id_generator import DeckIDGenerator
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.user.values.user_id import UserID


class DeckService:
    def __init__(self, deck_id_generator: DeckIDGenerator) -> None:
        self._id_generator: Final[DeckIDGenerator] = deck_id_generator

    def create_deck(
        self,
        user_id: UserID,
        title: DeckTitle,
        description: str | None,
        deck_config_id: DeckConfigID,
        is_public: bool,
    ) -> Deck:
        """Returns new deck object."""
        deck_id = self._id_generator()
        return Deck(
            id=deck_id,
            title=title,
            description=description,
            owner_id=user_id,
            deck_config_id=deck_config_id,
            is_public=is_public,
        )

    def copy_deck(self, deck: Deck, new_user_id: UserID) -> Deck:
        """Returns copy of deck object."""
        return Deck(
            id=self._id_generator(),
            owner_id=new_user_id,
            title=deck.title,
            description=deck.description,
            deck_config_id=deck.deck_config_id,
            is_public=deck.is_public,
        )
