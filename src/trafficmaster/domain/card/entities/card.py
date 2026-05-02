from dataclasses import dataclass

from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.deck_id import DeckID


@dataclass
class Card(BaseEntity[CardID]):
    deck_id: DeckID
    question: CardQuestion
    answer: CardAnswer
    image_path: str | None
    tags: list[CardTag]
