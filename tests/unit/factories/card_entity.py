from tests.unit.factories.values import (
    create_card_answer,
    create_card_id,
    create_card_question,
    create_deck_id,
)
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.deck.values.deck_id import DeckID


def create_card(
    card_id: CardID | None = None,
    deck_id: DeckID | None = None,
    question: CardQuestion | None = None,
    answer: CardAnswer | None = None,
    image_path: str | None = None,
    tags: list[CardTag] | None = None,
) -> Card:
    return Card(
        id=card_id or create_card_id(),
        deck_id=deck_id or create_deck_id(),
        question=question or create_card_question(),
        answer=answer or create_card_answer(),
        image_path=image_path,
        tags=tags if tags is not None else [],
    )
