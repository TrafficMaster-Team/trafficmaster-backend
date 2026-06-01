import pytest

from trafficmaster.domain.deck.errors.deck_config import (
    NewGreaterThanReviewedError,
    TooBigCardLimitError,
    TooSmallCardLimitError,
)
from trafficmaster.domain.deck.values.daily_limits import (
    MAX_CARDS_REPETITION,
    DailyLimits,
)


def test_accepts_default_limits() -> None:
    sut = DailyLimits(new_cards_per_day=20, max_reviews_per_day=200)

    assert sut.new_cards_per_day == 20
    assert sut.max_reviews_per_day == 200
    assert sut.reviews_dont_bury_new is False


def test_accepts_boundary_limits() -> None:
    sut = DailyLimits(new_cards_per_day=MAX_CARDS_REPETITION, max_reviews_per_day=MAX_CARDS_REPETITION)

    assert sut.new_cards_per_day == MAX_CARDS_REPETITION


def test_rejects_new_greater_than_reviews() -> None:
    with pytest.raises(NewGreaterThanReviewedError):
        DailyLimits(new_cards_per_day=300, max_reviews_per_day=200)


def test_rejects_too_small_limit() -> None:
    with pytest.raises(TooSmallCardLimitError):
        DailyLimits(new_cards_per_day=0, max_reviews_per_day=200)


def test_rejects_too_big_limit() -> None:
    with pytest.raises(TooBigCardLimitError):
        DailyLimits(new_cards_per_day=MAX_CARDS_REPETITION + 1, max_reviews_per_day=MAX_CARDS_REPETITION + 1)


def test_str_representation() -> None:
    sut = DailyLimits(new_cards_per_day=20, max_reviews_per_day=200)

    assert str(sut) == "20 new / 200 reviews"
