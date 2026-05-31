from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.domain.card_progress.values.card_state import CardState


class ReadCardProgressResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    id: UUID = Field(title="Card progress ID", description="Unique card progress ID in system")
    user_id: UUID = Field(title="User ID", description="The ID of the user the progress belongs to")
    card_id: UUID = Field(title="Card ID", description="The ID of the card the progress belongs to")
    state: CardState = Field(title="State", description="The current card state")
    ease_factor: float = Field(title="Ease factor", description="The current ease factor")
    interval: int = Field(title="Interval", description="The current interval in days")
    repetitions: int = Field(title="Repetitions", description="The number of successful repetitions")
    next_review_at: datetime | None = Field(
        default=None, title="Next review at", description="When the card is next due"
    )
