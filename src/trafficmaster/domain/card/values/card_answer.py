from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.card.errors.card import CardAnswerEmptyError, TooLongAnswerError, TooShortAnswerError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MINIMUM_CARD_ANSWER: Final[int] = 1
MAXIMUM_CARD_ANSWER: Final[int] = 5000


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class CardAnswer(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:

        if len(self.value) == 0 or self.value.isspace():
            msg = "Answer cannot be empty"
            raise CardAnswerEmptyError(msg)

        if len(self.value) > MAXIMUM_CARD_ANSWER:
            msg = f"Answer cannot be more than {MAXIMUM_CARD_ANSWER}"
            raise TooLongAnswerError(msg)

        if len(self.value) < MINIMUM_CARD_ANSWER:
            msg = f"Answer cannot be less than {MINIMUM_CARD_ANSWER}"
            raise TooShortAnswerError(msg)

    @override
    def __str__(self) -> str:
        return self.value
