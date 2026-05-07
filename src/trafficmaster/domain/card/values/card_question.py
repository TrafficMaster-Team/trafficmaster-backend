from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.card.errors.card import (
    CardQuestionEmptyError,
    TooLongQuestionError,
    TooShortQuestionError,
)
from trafficmaster.domain.common.values.base_value import BaseValueObject

MINIMUM_CARD_QUESTION: Final[int] = 1
MAXIMUM_CARD_QUESTION: Final[int] = 500


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class CardQuestion(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:

        if not self.value.strip():
            msg = "Question value must not be empty"
            raise CardQuestionEmptyError(msg)

        if len(self.value) < MINIMUM_CARD_QUESTION:
            msg = f"Question value must be at least {MINIMUM_CARD_QUESTION} character(s)"
            raise TooShortQuestionError(msg)

        if len(self.value) > MAXIMUM_CARD_QUESTION:
            msg = f"Question value must not be more than {MAXIMUM_CARD_QUESTION} characters"
            raise TooLongQuestionError(msg)

    @override
    def __str__(self) -> str:
        return self.value
