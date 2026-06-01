import pytest

from trafficmaster.domain.card_progress.errors.card_progress import TooLowEaseFactorError
from trafficmaster.domain.deck.errors.deck_config import (
    HardIntervalNotLessThanEaseFactorError,
    InvalidIntervalModifierError,
    InvalidNewIntervalError,
    TooLowEasyFactorError,
    TooLowMaxIntervalError,
)
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig


def _valid_kwargs() -> dict[str, float]:
    return {
        "max_interval": 36500,
        "ease_factor": 2.5,
        "easy_factor": 1.3,
        "interval_modifier": 1.0,
        "hard_interval": 1.2,
        "new_interval": 0.0,
    }


def test_accepts_valid_config() -> None:
    sut = AdvancedConfig(**_valid_kwargs())

    assert sut.max_interval == 36500
    assert sut.ease_factor == 2.5


def test_rejects_too_low_max_interval() -> None:
    with pytest.raises(TooLowMaxIntervalError):
        AdvancedConfig(**{**_valid_kwargs(), "max_interval": 0})


def test_rejects_too_low_ease_factor() -> None:
    with pytest.raises(TooLowEaseFactorError):
        AdvancedConfig(**{**_valid_kwargs(), "ease_factor": 1.2})


def test_rejects_too_low_easy_factor() -> None:
    with pytest.raises(TooLowEasyFactorError):
        AdvancedConfig(**{**_valid_kwargs(), "easy_factor": 0.5})


def test_rejects_non_positive_interval_modifier() -> None:
    with pytest.raises(InvalidIntervalModifierError):
        AdvancedConfig(**{**_valid_kwargs(), "interval_modifier": 0.0})


def test_rejects_hard_interval_not_less_than_ease() -> None:
    with pytest.raises(HardIntervalNotLessThanEaseFactorError):
        AdvancedConfig(**{**_valid_kwargs(), "hard_interval": 3.0})


@pytest.mark.parametrize("new_interval", [pytest.param(1.5, id="above_one"), pytest.param(-0.5, id="below_zero")])
def test_rejects_new_interval_out_of_range(new_interval: float) -> None:
    with pytest.raises(InvalidNewIntervalError):
        AdvancedConfig(**{**_valid_kwargs(), "new_interval": new_interval})
