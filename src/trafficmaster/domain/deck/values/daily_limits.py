from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import (
    NewGreaterThanReviewedError,
    TooBigCardLimitError,
    TooSmallCardLimitError,
)

MAX_CARDS_REPETITION: Final[int] = 999
MIN_CARDS_REPETITION: Final[int] = 1


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class DailyLimits(BaseValueObject):
    new_cards_per_day: int = 20
    max_reviews_per_day: int = 200
    reviews_dont_bury_new: bool = False

    @override
    def _validate(self) -> None:
        if self.new_cards_per_day > self.max_reviews_per_day:
            msg = "Maximum number of new cards per day cannot be greater than the maximum number of reviews per day."
            raise NewGreaterThanReviewedError(msg)

        if self.new_cards_per_day < MIN_CARDS_REPETITION or self.max_reviews_per_day < MIN_CARDS_REPETITION:
            msg = "Minimum number of cards per day cannot be less than 1"
            raise TooBigCardLimitError(msg)

        if self.new_cards_per_day > MAX_CARDS_REPETITION or self.max_reviews_per_day > MAX_CARDS_REPETITION:
            msg = "Maximum number of cards per day cannot be greater than 999."
            raise TooSmallCardLimitError(msg)

    @override
    def __str__(self) -> str:
        return f"{self.new_cards_per_day} new / {self.max_reviews_per_day} reviews"
