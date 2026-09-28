from trafficmaster.domain.card.entities.answer_option import AnswerOption
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.ports.answer_option_id_generator import AnswerOptionIDGenerator
from trafficmaster.domain.card.ports.card_id_generator import CardIDGenerator
from trafficmaster.domain.card.values.card_hint import CardHint
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.deck.values.deck_id import DeckID


class CardService:
    def __init__(
        self,
        id_generator: CardIDGenerator,
        answer_option_id_generator: AnswerOptionIDGenerator,
    ) -> None:
        self._id_generator = id_generator
        self._answer_option_id_generator = answer_option_id_generator

    def create_answer_option(self, text: str, is_correct: bool, rationale: str) -> AnswerOption:
        return AnswerOption(
            id=self._answer_option_id_generator(),
            text=text,
            is_correct=is_correct,
            rationale=rationale,
        )

    def create_card(
        self,
        deck_id: DeckID,
        question: CardQuestion,
        answer_options: list[AnswerOption],
        hint: CardHint,
        tags: list[CardTag] | None = None,
        image_path: str | None = None,
    ) -> Card:

        card_id = self._id_generator()
        return Card(
            id=card_id,
            question=question,
            deck_id=deck_id,
            answer_options=answer_options,
            hint=hint,
            tags=tags or [],
            image_path=image_path,
        )

    def copy_card(self, card: Card, new_deck_id: DeckID) -> Card:
        """Returns copy of card object placed into another deck."""
        return Card(
            id=self._id_generator(),
            deck_id=new_deck_id,
            question=card.question,
            answer_options=[
                self.create_answer_option(
                    text=option.text,
                    is_correct=option.is_correct,
                    rationale=option.rationale,
                )
                for option in card.answer_options
            ],
            hint=card.hint,
            image_path=card.image_path,
            tags=list(card.tags),
        )
