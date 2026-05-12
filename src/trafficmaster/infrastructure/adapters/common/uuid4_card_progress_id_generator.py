import uuid
from typing import override

from trafficmaster.domain.card_progress.ports.card_progress_id_generator import CardProgressIDGenerator
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID


class UUID4CardProgressIdGenerator(CardProgressIDGenerator):
    @override
    def __call__(self) -> CardProgressID:
        return CardProgressID(uuid.uuid4())
