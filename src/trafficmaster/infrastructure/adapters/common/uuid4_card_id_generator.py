import uuid
from typing import override

from trafficmaster.domain.card.ports.card_id_generator import CardIDGenerator
from trafficmaster.domain.card.values.card_id import CardID


class UUID4CardIdGenerator(CardIDGenerator):
    @override
    def __call__(self) -> CardID:
        return CardID(uuid.uuid4())
