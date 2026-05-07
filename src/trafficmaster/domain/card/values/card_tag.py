from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.card.errors.card import EmptyCardTagError, TooLongCardTagError, TooShortCardTagError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MINIMUM_CARD_TAG: Final[int] = 1
MAXIMUM_CARD_TAG: Final[int] = 50


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class CardTag(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:

        if not self.value.strip():
            msg = "Card tag must not be empty"
            raise EmptyCardTagError(msg)

        if len(self.value) < MINIMUM_CARD_TAG:
            msg = f"Card tag must be at least {MINIMUM_CARD_TAG} character(s)"
            raise TooShortCardTagError(msg)

        if len(self.value) > MAXIMUM_CARD_TAG:
            msg = f"Card tag must be at most {MAXIMUM_CARD_TAG} characters"
            raise TooLongCardTagError(msg)

    @override
    def __str__(self) -> str:
        return self.value
