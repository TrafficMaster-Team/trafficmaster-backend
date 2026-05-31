from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


class ReviewLogResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    id: UUID = Field(title="Review log ID", description="Unique review log ID in system")
    user_id: UUID = Field(title="User ID", description="The ID of the user who made the review")
    card_id: UUID = Field(title="Card ID", description="The ID of the reviewed card")
    rating: ReviewRating = Field(title="Rating", description="The review rating: AGAIN=1, HARD=2, GOOD=3, EASY=4")
    reviewed_at: datetime = Field(title="Reviewed at", description="When the review happened")


class ReviewLogsResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    logs: list[ReviewLogResponseSchema] = Field(default=[], title="Review logs", description="The review log entries")
