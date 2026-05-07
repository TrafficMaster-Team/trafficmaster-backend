from dataclasses import dataclass
from datetime import datetime

from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.interval import Interval
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.user.values.user_id import UserID


@dataclass(eq=False)
class CardProgress(BaseEntity[CardProgressID]):
    """
    Tracks SRS state of a card for a specific user.
    params:
        user_id: id of the user,
        card_id: id of the card being tracked,
        ease_factor: current ease multiplier (min 1.3),
        interval: days until next review (used in REVIEW state),
        repetitions: current step index in LEARNING/RELEARNING, successful review count in REVIEW,
        state: NEW, LEARNING, REVIEW, or RELEARNING,
        next_review_at: scheduled review datetime, None for NEW cards.
    """

    user_id: UserID
    card_id: CardID
    ease_factor: EaseFactor
    interval: Interval
    repetitions: int
    state: CardState
    next_review_at: datetime | None
