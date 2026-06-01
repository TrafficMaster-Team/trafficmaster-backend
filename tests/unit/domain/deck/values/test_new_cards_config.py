import pytest

from trafficmaster.domain.card_progress.errors.card_progress import TooLowIntervalError
from trafficmaster.domain.deck.errors.deck_config import (
    LearningIntervalGreaterGraduatingError,
    NotEnoughLearningStepsError,
    TooLowStepIntervalError,
)
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder, NewCardsConfig


def test_accepts_valid_config() -> None:
    sut = NewCardsConfig(
        learning_steps=[1, 10],
        graduating_interval=1,
        easy_interval=4,
        new_card_order=NewCardOrder.SEQUENTIAL,
    )

    assert sut.learning_steps == [1, 10]
    assert sut.graduating_interval == 1


def test_rejects_empty_learning_steps() -> None:
    with pytest.raises(NotEnoughLearningStepsError):
        NewCardsConfig(
            learning_steps=[],
            graduating_interval=1,
            easy_interval=4,
            new_card_order=NewCardOrder.SEQUENTIAL,
        )


def test_rejects_last_step_greater_than_graduating() -> None:
    # 2880 minutes is two days, longer than the one-day graduating interval
    with pytest.raises(LearningIntervalGreaterGraduatingError):
        NewCardsConfig(
            learning_steps=[2880],
            graduating_interval=1,
            easy_interval=4,
            new_card_order=NewCardOrder.SEQUENTIAL,
        )


def test_rejects_too_low_easy_interval() -> None:
    with pytest.raises(TooLowIntervalError):
        NewCardsConfig(
            learning_steps=[1],
            graduating_interval=1,
            easy_interval=0,
            new_card_order=NewCardOrder.SEQUENTIAL,
        )


def test_rejects_too_low_step_interval() -> None:
    with pytest.raises(TooLowStepIntervalError):
        NewCardsConfig(
            learning_steps=[0],
            graduating_interval=1,
            easy_interval=4,
            new_card_order=NewCardOrder.SEQUENTIAL,
        )
