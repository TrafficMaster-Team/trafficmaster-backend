import pytest

from trafficmaster.domain.card_progress.errors.card_progress import TooLowEaseFactorError
from trafficmaster.domain.card_progress.values.ease_factor import MIN_EASE_FACTOR, EaseFactor


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MIN_EASE_FACTOR, id="min_boundary"),
        pytest.param(2.5, id="default"),
        pytest.param(5.0, id="high"),
    ],
)
def test_accepts_valid_ease_factor(value: float) -> None:
    sut = EaseFactor(value)

    assert sut.value == value
    assert str(sut) == str(value)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MIN_EASE_FACTOR - 0.01, id="just_below_min"),
        pytest.param(0.0, id="zero"),
        pytest.param(-1.0, id="negative"),
    ],
)
def test_rejects_too_low_ease_factor(value: float) -> None:
    with pytest.raises(TooLowEaseFactorError):
        EaseFactor(value)


def test_ease_factor_equality() -> None:
    assert EaseFactor(2.5) == EaseFactor(2.5)
    assert EaseFactor(2.5) != EaseFactor(2.6)
