from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise
from typing import override

from trafficmaster.domain.card_progress.errors.card_progress import TooLowIntervalError
from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import (
    EasyIntervalLessThanGraduatingError,
    LearningIntervalGreaterGraduatingError,
    NotEnoughLearningStepsError,
    StepsNotIncreasingError,
    TooLowStepIntervalError,
)
from trafficmaster.domain.deck.values._constants import MIN_INTERVAL_LENGTH


class NewCardOrder(StrEnum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class NewCardsConfig(BaseValueObject):
    learning_steps: list[int]
    graduating_interval: int
    easy_interval: int
    new_card_order: NewCardOrder

    @override
    def _validate(self) -> None:

        if len(self.learning_steps) < 1:
            msg = "You must specify at least one learning step"
            raise NotEnoughLearningStepsError(msg)

        last_step_in_days = self.learning_steps[-1] / (60 * 24)
        if last_step_in_days > self.graduating_interval:
            msg = "Last learning interval cannot be greater than graduating interval"
            raise LearningIntervalGreaterGraduatingError(msg)

        if self.graduating_interval < MIN_INTERVAL_LENGTH or self.easy_interval < MIN_INTERVAL_LENGTH:
            msg = "Graduating and easy intervals cannot be less than 1 day"
            raise TooLowIntervalError(msg)

        if self.easy_interval < self.graduating_interval:
            msg = "Easy interval cannot be less than graduating interval"
            raise EasyIntervalLessThanGraduatingError(msg)

        if any(step < MIN_INTERVAL_LENGTH for step in self.learning_steps):
            msg = "One of the learning steps cannot be less than minimum interval length (1m)"
            raise TooLowStepIntervalError(msg)

        if any(current >= following for current, following in pairwise(self.learning_steps)):
            msg = "Learning steps must be strictly increasing"
            raise StepsNotIncreasingError(msg)

    @override
    def __str__(self) -> str:
        return (
            f"learning steps: {' '.join(str(s) for s in self.learning_steps)}"
            f" graduating interval: {self.graduating_interval}"
        )
