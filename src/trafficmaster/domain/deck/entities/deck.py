from dataclasses import dataclass

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.user.values.user_id import UserID


@dataclass
class Deck(BaseEntity[DeckID]):
    """
    Deck entity
    params:
        owner_id: id of a user,
        title: title of a deck,
        deck_config: id of a deck configuration,
        description: description of a deck,
        is_public: is this a public deck.
    """

    owner_id: UserID
    deck_config: DeckConfigID
    title: DeckTitle
    description: str | None
    is_public: bool
