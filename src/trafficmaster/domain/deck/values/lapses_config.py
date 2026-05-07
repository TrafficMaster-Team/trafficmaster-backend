from dataclasses import dataclass
from enum import StrEnum
from typing import override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import (
    NotEnoughLearningStepsError,
    TooLowStepIntervalError,
    TooSmallLeechThresholdError,
    TooSmallMinRepeatIntervalError,
)


class LeechAction(StrEnum):
    TAG_ONLY = "tag_only"
    SUSPEND = "suspend"


MIN_INTERVAL_LENGTH = 1


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class LapsesConfig(BaseValueObject):
    relearning_steps: list[int]
    min_interval: int
    leech_threshold: int
    leech_action: LeechAction

    @override
    def _validate(self) -> None:
        if len(self.relearning_steps) < 1:
            msg = "You must specify at least one relearning step"
            raise NotEnoughLearningStepsError(msg)

        if self.leech_threshold < 1:
            msg = "Lapses config: leech_threshold must be greater than 0."
            raise TooSmallLeechThresholdError(msg)

        if self.min_interval < 1:
            msg = "Lapses config: minimum interval for repeat cards must be greater than 0."
            raise TooSmallMinRepeatIntervalError(msg)

        if any(step < MIN_INTERVAL_LENGTH for step in self.relearning_steps):
            msg = "One of the learning steps cannot be less than minimum interval length (1m)"
            raise TooLowStepIntervalError(msg)

    @override
    def __str__(self) -> str:
        return (
            f"Relearning steps: {' '.join(str(s) for s in self.relearning_steps)},"
            f"min_interval: {self.min_interval},"
            f"leech_threshold: {self.leech_threshold},"
            f"leech_action: {self.leech_action}"
        )
