from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from trafficmaster.domain.card_progress.values.card_state import CardState


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewCardView:
    card_progress_id: UUID
    review_log_id: UUID
    state: CardState
    interval: int
    next_review_at: datetime | None
