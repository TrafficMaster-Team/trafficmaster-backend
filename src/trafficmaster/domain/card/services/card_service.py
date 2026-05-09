from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.ports.card_id_generator import CardIDGenerator
from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.deck.values.deck_id import DeckID


class CardService:
    def __init__(self, id_generator: CardIDGenerator) -> None:
        self._id_generator = id_generator

    def create_card(
        self,
        deck_id: DeckID,
        question: CardQuestion,
        answer: CardAnswer,
        tags: list[CardTag] | None = None,
        image_path: str | None = None,
    ) -> Card:

        card_id = self._id_generator()
        return Card(
            id=card_id, question=question, deck_id=deck_id, answer=answer, tags=tags or [], image_path=image_path
        )

    def copy_card(self, card: Card, new_deck_id: DeckID) -> Card:
        """Returns copy of card object placed into another deck."""
        return Card(
            id=self._id_generator(),
            deck_id=new_deck_id,
            question=card.question,
            answer=card.answer,
            image_path=card.image_path,
            tags=list(card.tags),
        )
