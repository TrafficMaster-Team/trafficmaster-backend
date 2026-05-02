from dataclasses import dataclass
from typing import override

from trafficmaster.domain.card_progress.errors.card_progress import TooLowIntervalError
from trafficmaster.domain.common.values.base_value import BaseValueObject

MIN_INTERVAL = 1


@dataclass(eq=True, frozen=True, unsafe_hash=True)
class Interval(BaseValueObject):
    value: int

    @override
    def _validate(self) -> None:
        if self.value < MIN_INTERVAL:
            msg = f"Interval cannot be less than {MIN_INTERVAL}"
            raise TooLowIntervalError(msg)

    @override
    def __str__(self) -> str:
        return str(self.value)
