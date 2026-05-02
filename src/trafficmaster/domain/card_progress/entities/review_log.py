from dataclasses import dataclass
from datetime import datetime

from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.user.values.user_id import UserID


@dataclass
class ReviewLog(BaseEntity[ReviewLogID]):
    user_id: UserID
    card_id: CardID
    rating: ReviewRating
    reviewed_at: datetime
