from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.ports.card_id_generator import CardIdGenerator
from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.deck.values.deck_id import DeckID


class CardService:
    def __init__(self, id_generator: CardIdGenerator) -> None:
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
