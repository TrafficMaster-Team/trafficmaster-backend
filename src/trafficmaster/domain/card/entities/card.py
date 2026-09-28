from dataclasses import dataclass, field
from datetime import UTC, datetime

from trafficmaster.domain.card.errors.card import (
    CardTagNotFoundError,
    DuplicateCardTagError,
    EmptyAnswerOptionsError,
    InvalidCorrectAnswerCountError,
)
from trafficmaster.domain.card.values.answer_option import AnswerOption
from trafficmaster.domain.card.values.card_hint import CardHint
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.deck_id import DeckID


@dataclass(eq=False)
class Card(BaseEntity[CardID]):
    """
    Card entity.
    params:
        deck_id: id of the deck this card belongs to,
        question: front side of the card,
        answer_options: possible answers with correctness and rationale,
        hint: hint shown for the question,
        image_path: optional path to an attached image,
        tags: list of tags for filtering and organization.
    """

    deck_id: DeckID
    question: CardQuestion
    answer_options: list[AnswerOption]
    hint: CardHint
    image_path: str | None
    tags: list[CardTag] = field(default_factory=list)

    def change_deck(self, deck_id: DeckID) -> None:
        self.deck_id = deck_id
        self.updated_at = datetime.now(UTC)

    def change_question(self, question: CardQuestion) -> None:
        self.question = question
        self.updated_at = datetime.now(UTC)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._validate_answer_options(self.answer_options)

    @staticmethod
    def _validate_answer_options(answer_options: list[AnswerOption]) -> None:
        if not answer_options:
            msg = "Card must have at least one answer option"
            raise EmptyAnswerOptionsError(msg)
        if sum(option.is_correct for option in answer_options) != 1:
            msg = "Card must have exactly one correct answer option"
            raise InvalidCorrectAnswerCountError(msg)

    def change_answer_options(self, answer_options: list[AnswerOption]) -> None:
        self._validate_answer_options(answer_options)
        self.answer_options = answer_options
        self.updated_at = datetime.now(UTC)

    def change_hint(self, hint: CardHint) -> None:
        self.hint = hint
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
