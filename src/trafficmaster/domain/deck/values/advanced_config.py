from dataclasses import dataclass
from typing import override

from trafficmaster.domain.card_progress.errors.card_progress import TooLowEaseFactorError
from trafficmaster.domain.card_progress.values.ease_factor import MIN_EASE_FACTOR
from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import (
    HardIntervalNotLessThanEaseFactorError,
    InvalidIntervalModifierError,
    InvalidNewIntervalError,
    TooLowEasyFactorError,
    TooLowMaxIntervalError,
)

MIN_EASY_FACTOR = 1.0
MIN_MAX_INTERVAL = 1


@dataclass(eq=True, frozen=True)
class AdvancedConfig(BaseValueObject):
    max_interval: int
    ease_factor: float
    easy_factor: float
    interval_modifier: float
    hard_interval: float
    new_interval: float

    @override
    def _validate(self) -> None:
        if self.max_interval < MIN_MAX_INTERVAL:
            msg = "Interval cannot be less than minimum interval length (1)"
            raise TooLowMaxIntervalError(msg)

        if self.ease_factor < MIN_EASE_FACTOR:
            msg = f"Ease factor cannot be less than minimum value ({MIN_EASE_FACTOR})"
            raise TooLowEaseFactorError(msg)

        if self.easy_factor < MIN_EASY_FACTOR:
            msg = f"Easy factor cannot be less than minimum value ({MIN_EASY_FACTOR})"
            raise TooLowEasyFactorError(msg)

        if self.interval_modifier <= 0:
            msg = "Interval modifier must be greater than 0"
            raise InvalidIntervalModifierError(msg)

        if self.hard_interval >= self.ease_factor:
            msg = f"Hard interval cannot be greater than ease factor ({self.hard_interval})"
            raise HardIntervalNotLessThanEaseFactorError(msg)

        if not (0.0 <= self.new_interval <= 1.0):
            msg = f"New interval must be between 0 and 1 ({self.new_interval})"
            raise InvalidNewIntervalError(msg)

    @override
    def __str__(self) -> str:
        return (
            f"max_interval: {self.max_interval}, "
            f"ease_factor: {self.ease_factor}, "
            f"easy_factor: {self.easy_factor}, "
            f"interval_modifier: {self.interval_modifier}, "
            f"hard_interval: {self.hard_interval}, "
            f"new_interval: {self.new_interval}"
        )
