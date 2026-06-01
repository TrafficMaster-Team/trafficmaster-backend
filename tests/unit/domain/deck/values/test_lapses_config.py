import pytest

from trafficmaster.domain.deck.errors.deck_config import (
    NotEnoughLearningStepsError,
    TooLowStepIntervalError,
    TooSmallLeechThresholdError,
    TooSmallMinRepeatIntervalError,
)
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig, LeechAction


def test_accepts_valid_config() -> None:
    sut = LapsesConfig(
        relearning_steps=[10],
        min_interval=1,
        leech_threshold=8,
        leech_action=LeechAction.SUSPEND,
    )

    assert sut.relearning_steps == [10]
    assert sut.leech_action == LeechAction.SUSPEND


def test_rejects_empty_relearning_steps() -> None:
    with pytest.raises(NotEnoughLearningStepsError):
        LapsesConfig(relearning_steps=[], min_interval=1, leech_threshold=8, leech_action=LeechAction.SUSPEND)


def test_rejects_too_small_leech_threshold() -> None:
    with pytest.raises(TooSmallLeechThresholdError):
        LapsesConfig(relearning_steps=[10], min_interval=1, leech_threshold=0, leech_action=LeechAction.SUSPEND)


def test_rejects_too_small_min_interval() -> None:
    with pytest.raises(TooSmallMinRepeatIntervalError):
        LapsesConfig(relearning_steps=[10], min_interval=0, leech_threshold=8, leech_action=LeechAction.SUSPEND)


def test_rejects_too_low_step_interval() -> None:
    with pytest.raises(TooLowStepIntervalError):
        LapsesConfig(relearning_steps=[0], min_interval=1, leech_threshold=8, leech_action=LeechAction.TAG_ONLY)
