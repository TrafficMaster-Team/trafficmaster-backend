from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.application.common.views.card_progress.review_queue_item import ReviewReason
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.presentation.http.v1.routes.card.create_card.schemas import AnswerOptionSchema


class ReviewQueueItemSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True, populate_by_name=True)

    card_id: UUID = Field(title="Card ID", description="The ID of the card")
    question: str = Field(title="Question", description="The card question")
    answer_options: list[AnswerOptionSchema] = Field(
        alias="answerOptions", title="Answer options", description="Possible card answers"
    )
    hint: str = Field(title="Hint", description="The card hint")
    image_path: str | None = Field(default=None, title="Image path", description="Optional image path")
    tags: list[str] = Field(default=[], title="Tags", description="The card tags")
    state: CardState | None = Field(default=None, title="State", description="The card state, if any")
    interval: int | None = Field(default=None, title="Interval", description="The current interval in days")
    repetitions: int | None = Field(default=None, title="Repetitions", description="Successful repetitions")
    next_review_at: datetime | None = Field(default=None, title="Next review at", description="When the card is due")
    reason: ReviewReason = Field(title="Reason", description="Why the card is in the queue")


class ReviewQueueResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[ReviewQueueItemSchema] = Field(default=[], title="Items", description="The review queue items")
