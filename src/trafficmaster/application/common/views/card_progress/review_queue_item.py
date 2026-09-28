from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from trafficmaster.application.common.views.card.answer_option import AnswerOptionView
from trafficmaster.domain.card_progress.values.card_state import CardState


class ReviewReason(StrEnum):
    LEARNING = "learning"
    REVIEW = "review"
    NEW = "new"


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewQueueItemView:
    card_id: UUID
    question: str
    answer_options: list[AnswerOptionView]
    hint: str
    image_path: str | None
    tags: list[str]
    state: CardState | None
    interval: int | None
    repetitions: int | None
    next_review_at: datetime | None
    reason: ReviewReason
