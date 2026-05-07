from dataclasses import dataclass

from trafficmaster.domain.card.errors.card import EmptyCardTagError, TooLongCardTagError, TooShortCardTagError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MINIMUM_CARD_TAG = 1
MAXIMUM_CARD_TAG = 50


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class CardTag(BaseValueObject):
    value: str

    def _validate(self) -> None:

        if not self.value.strip():
            msg = "Card tag must not be empty"
            raise EmptyCardTagError(msg)

        if len(self.value) > MAXIMUM_CARD_TAG:
            msg = f"Card tag value must be less than {MAXIMUM_CARD_TAG}"
            raise TooLongCardTagError(msg)

        if len(self.value) < MINIMUM_CARD_TAG:
            msg = f"Card tag value must be more than {MINIMUM_CARD_TAG}"
            raise TooShortCardTagError(msg)

    def __str__(self) -> str:
        return self.value
