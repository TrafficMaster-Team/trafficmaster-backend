from dataclasses import dataclass, field
from datetime import UTC, datetime

from trafficmaster.domain.card.errors.card import CardTagNotFoundError, DuplicateCardTagError
from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.deck_id import DeckID


@dataclass
class Card(BaseEntity[CardID]):
    """
    Card entity.
    params:
        deck_id: id of the deck this card belongs to,
        question: front side of the card,
        answer: back side of the card,
        image_path: optional path to an attached image,
        tags: list of tags for filtering and organization.
    """

    deck_id: DeckID
    question: CardQuestion
    answer: CardAnswer
    image_path: str | None
    tags: list[CardTag] = field(default_factory=list)

    def change_deck(self, deck_id: DeckID) -> None:
        self.deck_id = deck_id
        self.updated_at = datetime.now(UTC)

    def change_question(self, question: CardQuestion) -> None:
        self.question = question
        self.updated_at = datetime.now(UTC)

    def change_answer(self, answer: CardAnswer) -> None:
        self.answer = answer
        self.updated_at = datetime.now(UTC)

    def change_image_path(self, image_path: str | None) -> None:
        self.image_path = image_path
        self.updated_at = datetime.now(UTC)

    def add_tag(self, tag: CardTag) -> None:
        if tag in self.tags:
            msg = "Tag already exists"
            raise DuplicateCardTagError(msg)
        self.tags.append(tag)
        self.updated_at = datetime.now(UTC)

    def remove_tag(self, tag: CardTag) -> None:
        if tag not in self.tags:
            msg = "Tag not found"
            raise CardTagNotFoundError(msg)
        self.tags.remove(tag)
        self.updated_at = datetime.now(UTC)
