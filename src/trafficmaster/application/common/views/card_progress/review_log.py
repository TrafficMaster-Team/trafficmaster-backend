from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewLogView:
    id: UUID
    user_id: UUID
    card_id: UUID
    rating: ReviewRating
    reviewed_at: datetime
