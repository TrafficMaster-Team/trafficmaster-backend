from dataclasses import dataclass
from datetime import datetime

from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.interval import Interval
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.user.values.user_id import UserID


@dataclass
class CardProgress(BaseEntity[CardProgressID]):
    user_id: UserID
    card_id: CardID
    ease_factor: EaseFactor
    interval: Interval
    repetitions: int
    state: CardState
    next_review_at: datetime | None
