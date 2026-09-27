from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.card.errors.card import TooLongAnswerError, TooShortAnswerError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MIN_CARD_ANSWER: Final[int] = 1
MAX_CARD_ANSWER: Final[int] = 500


@dataclass(frozen=True, eq=True)
class AnswerOption(BaseValueObject):
    text: str
    is_correct: bool

    @override
    def _validate(self) -> None:
        if self.text < MIN_CARD_ANSWER or self.text.isspace():
            msg = "Answer option text must be non-empty."
            raise TooShortAnswerError(msg)

        if self.text > MAX_CARD_ANSWER:
            msg = f"Answer option text must be at most {MAX_CARD_ANSWER} characters long."
            raise TooLongAnswerError(msg)

    @override
    def __str__(self) -> str:
        return self.text
