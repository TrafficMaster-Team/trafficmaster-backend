import pytest

from trafficmaster.domain.card_progress.errors.card_progress import TooLowIntervalError
from trafficmaster.domain.card_progress.values.interval import MIN_INTERVAL, Interval


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MIN_INTERVAL, id="min_boundary"),
        pytest.param(30, id="typical"),
        pytest.param(36500, id="large"),
    ],
)
def test_accepts_valid_interval(value: int) -> None:
    sut = Interval(value)

    assert sut.value == value
    assert str(sut) == str(value)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MIN_INTERVAL - 1, id="zero"),
        pytest.param(-5, id="negative"),
    ],
)
def test_rejects_too_low_interval(value: int) -> None:
    with pytest.raises(TooLowIntervalError):
        Interval(value)


def test_interval_equality() -> None:
    assert Interval(10) == Interval(10)
    assert Interval(10) != Interval(11)
