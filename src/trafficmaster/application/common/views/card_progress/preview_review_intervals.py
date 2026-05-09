from dataclasses import dataclass
from datetime import datetime

from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewPreviewItem:
    rating: ReviewRating
    state: CardState
    interval: int
    next_review_at: datetime | None


@dataclass(frozen=True, slots=True, kw_only=True)
class PreviewReviewIntervalsView:
    items: list[ReviewPreviewItem]
