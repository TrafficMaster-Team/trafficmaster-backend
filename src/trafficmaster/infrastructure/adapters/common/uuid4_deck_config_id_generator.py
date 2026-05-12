import uuid
from typing import override

from trafficmaster.domain.deck.ports.deck_config_id_generator import DeckConfigIDGenerator
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID


class UUID4DeckConfigIdGenerator(DeckConfigIDGenerator):
    @override
    def __call__(self) -> DeckConfigID:
        return DeckConfigID(uuid.uuid4())
