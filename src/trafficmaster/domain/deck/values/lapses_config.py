from dataclasses import dataclass
from itertools import pairwise
from typing import override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import (
    StepsNotIncreasingError,
    TooLowStepIntervalError,
    TooSmallMinRepeatIntervalError,
)
from trafficmaster.domain.deck.values._constants import MIN_INTERVAL_LENGTH


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class LapsesConfig(BaseValueObject):
    relearning_steps: list[int]
    min_interval: int

    @override
    def _validate(self) -> None:
        if self.min_interval < 1:
            msg = "Lapses config: minimum interval for repeat cards must be greater than 0."
            raise TooSmallMinRepeatIntervalError(msg)

        if any(step < MIN_INTERVAL_LENGTH for step in self.relearning_steps):
            msg = "One of the relearning steps cannot be less than minimum interval length (1m)"
            raise TooLowStepIntervalError(msg)

        if any(current >= following for current, following in pairwise(self.relearning_steps)):
            msg = "Relearning steps must be strictly increasing"
            raise StepsNotIncreasingError(msg)

    @override
    def __str__(self) -> str:
        return f"Relearning steps: {' '.join(str(s) for s in self.relearning_steps)}, min_interval: {self.min_interval}"
