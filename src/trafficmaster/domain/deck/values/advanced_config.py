from dataclasses import dataclass
from typing import override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import (
    HardIntervalNotLessThanEaseFactorError,
    InvalidIntervalModificatorError,
    InvalidNewIntervalError,
    TooLowEaseFactorError,
    TooLowMaxIntervalError,
)

MIN_EASE_FACTOR = 1.3
MIN_MAX_INTERVAL = 1


@dataclass(eq=True, frozen=True)
class AdvancedConfig(BaseValueObject):
    max_interval: int
    ease_factor: float
    easy_factor: float
    interval_modificator: float
    hard_interval: float
    new_interval: float

    @override
    def _validate(self) -> None:
        if self.max_interval < MIN_MAX_INTERVAL:
            msg = "Interval cannot be greater than minimum interval length (1)"
            raise TooLowMaxIntervalError(msg)

        if self.ease_factor < MIN_EASE_FACTOR:
            msg = "Easy interval cannot be less than minimum interval length (1.3)"
            raise TooLowEaseFactorError(msg)

        if self.interval_modificator <= 0:
            msg = "Interval modificator cannot be less than 0"
            raise InvalidIntervalModificatorError(msg)

        if self.hard_interval >= self.ease_factor:
            msg = f"Hard interval cannot be greater than ease factor ({self.hard_interval})"
            raise HardIntervalNotLessThanEaseFactorError(msg)

        if not (0.0 <= self.new_interval <= 1.0):
            msg = f"New interval cannot be greater than interval length ({self.new_interval})"
            raise InvalidNewIntervalError(msg)

    @override
    def __str__(self) -> str:
        return (
            f"Max_interval: {self.max_interval},"
            f"ease_factor: {self.ease_factor},"
            f"interval_modificator: {self.interval_modificator},"
            f"hard_interval: {self.hard_interval},"
            f"new_interval: {self.new_interval}"
        )
