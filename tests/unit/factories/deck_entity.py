from tests.unit.factories.values import (
    create_deck_config_id,
    create_deck_id,
    create_deck_title,
    create_user_id,
)
from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.user.values.user_id import UserID


def create_deck(
    deck_id: DeckID | None = None,
    owner_id: UserID | None = None,
    deck_config_id: DeckConfigID | None = None,
    title: DeckTitle | None = None,
    description: str | None = "A deck for studying",
    *,
    is_public: bool = False,
) -> Deck:
    return Deck(
        id=deck_id or create_deck_id(),
        owner_id=owner_id or create_user_id(),
        deck_config_id=deck_config_id or create_deck_config_id(),
        title=title or create_deck_title(),
        description=description,
        is_public=is_public,
    )
