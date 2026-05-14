from dataclasses import dataclass
from datetime import datetime

from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.user.values.user_id import UserID


@dataclass(eq=False)
class ReviewLog(BaseEntity[ReviewLogID]):
    """
    Record of a single card review event. Treated as append-only.
    params:
        user_id: id of the user who reviewed,
        card_id: id of the reviewed card,
        rating: AGAIN, HARD, GOOD, or EASY,
        card_state: state of the card at the moment of review, before scheduling,
        reviewed_at: exact datetime of the review.
    """

    user_id: UserID
    card_id: CardID
    rating: ReviewRating
    card_state: CardState
    reviewed_at: datetime
