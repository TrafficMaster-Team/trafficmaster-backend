from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.card.errors.card import TooLongCardHintError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MAX_CARD_HINT: Final[int] = 5000


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class CardHint(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if len(self.value) > MAX_CARD_HINT:
            msg = f"Card hint cannot be more than {MAX_CARD_HINT} characters"
            raise TooLongCardHintError(msg)

    @override
    def __str__(self) -> str:
        return self.value
