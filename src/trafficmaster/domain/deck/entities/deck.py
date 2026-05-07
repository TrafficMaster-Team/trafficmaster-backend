from dataclasses import dataclass

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.user.values.user_id import UserID


@dataclass(eq=False)
class Deck(BaseEntity[DeckID]):
    """
    Deck entity.
    params:
        owner_id: id of the deck owner,
        deck_config_id: id of the SRS configuration applied to this deck,
        title: display title of the deck,
        description: optional description,
        is_public: whether the deck is visible to other users.
    """

    owner_id: UserID
    deck_config_id: DeckConfigID
    title: DeckTitle
    description: str | None
    is_public: bool
