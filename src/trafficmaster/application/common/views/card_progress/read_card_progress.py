from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from trafficmaster.domain.card_progress.values.card_state import CardState


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadCardProgressView:
    id: UUID
    user_id: UUID
    card_id: UUID
    state: CardState
    ease_factor: float
    interval: int
    repetitions: int
    next_review_at: datetime | None
