from dataclasses import dataclass
from typing import override

from trafficmaster.domain.card_progress.errors.card_progress import TooLowEaseFactorError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MIN_EASE_FACTOR = 1.3


@dataclass(eq=True, frozen=True, unsafe_hash=True)
class EaseFactor(BaseValueObject):
    value: float

    @override
    def _validate(self) -> None:

        if self.value < MIN_EASE_FACTOR:
            msg = f"Ease factor cannot be less than {MIN_EASE_FACTOR}"
            raise TooLowEaseFactorError(msg)

    @override
    def __str__(self) -> str:
        return str(self.value)
