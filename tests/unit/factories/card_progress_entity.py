from datetime import UTC, datetime

from tests.unit.factories.values import (
    create_card_id,
    create_card_progress_id,
    create_ease_factor,
    create_interval,
    create_review_log_id,
    create_user_id,
)
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.interval import Interval
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.user.values.user_id import UserID


def create_card_progress(
    progress_id: CardProgressID | None = None,
    user_id: UserID | None = None,
    card_id: CardID | None = None,
    ease_factor: EaseFactor | None = None,
    interval: Interval | None = None,
    repetitions: int = 0,
    state: CardState = CardState.NEW,
    next_review_at: datetime | None = None,
) -> CardProgress:
    return CardProgress(
        id=progress_id or create_card_progress_id(),
        user_id=user_id or create_user_id(),
        card_id=card_id or create_card_id(),
        ease_factor=ease_factor or create_ease_factor(),
        interval=interval or create_interval(),
        repetitions=repetitions,
        state=state,
        next_review_at=next_review_at,
    )


def create_review_log(
    review_log_id: ReviewLogID | None = None,
    user_id: UserID | None = None,
    card_id: CardID | None = None,
    rating: ReviewRating = ReviewRating.GOOD,
    card_state: CardState = CardState.NEW,
    reviewed_at: datetime | None = None,
) -> ReviewLog:
    return ReviewLog(
        id=review_log_id or create_review_log_id(),
        user_id=user_id or create_user_id(),
        card_id=card_id or create_card_id(),
        rating=rating,
        card_state=card_state,
        reviewed_at=reviewed_at or datetime.now(UTC),
    )
