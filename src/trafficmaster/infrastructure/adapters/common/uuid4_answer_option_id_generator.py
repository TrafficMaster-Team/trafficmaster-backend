import uuid
from typing import override

from trafficmaster.domain.card.ports.answer_option_id_generator import AnswerOptionIDGenerator
from trafficmaster.domain.card.values.answer_option_id import AnswerOptionID


class UUID4AnswerOptionIDGenerator(AnswerOptionIDGenerator):
    @override
    def __call__(self) -> AnswerOptionID:
        return AnswerOptionID(uuid.uuid4())
