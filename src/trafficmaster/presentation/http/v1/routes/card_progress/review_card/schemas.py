from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


class ReviewCardRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    rating: ReviewRating = Field(
        title="Rating",
        description="The review rating: AGAIN=1, HARD=2, GOOD=3, EASY=4",
        examples=[ReviewRating.GOOD],
    )


class ReviewCardResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    card_progress_id: UUID = Field(title="Card progress ID", description="The ID of the updated card progress")
    review_log_id: UUID = Field(title="Review log ID", description="The ID of the created review log")
    state: CardState = Field(title="State", description="The new card state after the review")
    interval: int = Field(title="Interval", description="The new interval in days")
    next_review_at: datetime | None = Field(
        default=None,
        title="Next review at",
        description="When the card is next due",
    )
