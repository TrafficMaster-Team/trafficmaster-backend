import uuid
from typing import override

from trafficmaster.domain.deck.ports.deck_id_generator import DeckIDGenerator
from trafficmaster.domain.deck.values.deck_id import DeckID


class UUID4DeckIdGenerator(DeckIDGenerator):
    @override
    def __call__(self) -> DeckID:
        return DeckID(uuid.uuid4())
