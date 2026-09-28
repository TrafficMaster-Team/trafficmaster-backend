from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.card.values.answer_option_id import AnswerOptionID


class AnswerOptionIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> AnswerOptionID: ...
