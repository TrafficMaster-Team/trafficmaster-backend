from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


class ReviewPreviewItemSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    rating: ReviewRating = Field(title="Rating", description="The hypothetical rating: AGAIN=1, HARD=2, GOOD=3, EASY=4")
    state: CardState = Field(title="State", description="The resulting card state for this rating")
    interval: int = Field(title="Interval", description="The resulting interval in days")
    next_review_at: datetime | None = Field(default=None, title="Next review at", description="Resulting next due date")


class PreviewReviewIntervalsResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[ReviewPreviewItemSchema] = Field(
        default=[],
        title="Items",
        description="Preview of resulting intervals per rating",
    )
