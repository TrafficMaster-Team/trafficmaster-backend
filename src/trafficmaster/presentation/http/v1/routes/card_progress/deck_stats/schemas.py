from pydantic import BaseModel, ConfigDict, Field


class ReadDeckStatsResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    total_cards: int = Field(title="Total cards", description="Total number of cards in the deck")
    new_count: int = Field(title="New cards", description="Number of cards in the NEW state")
    learning_count: int = Field(title="Learning cards", description="Number of cards in the LEARNING/RELEARNING state")
    review_count: int = Field(title="Review cards", description="Number of cards in the REVIEW state")
    due_learning: int = Field(title="Due learning", description="Number of learning cards due now")
    due_review: int = Field(title="Due review", description="Number of review cards due now")
    new_available: int = Field(title="New available", description="Number of new cards available to study today")
    new_done_today: int = Field(title="New done today", description="Number of new cards studied today")
    reviews_done_today: int = Field(title="Reviews done today", description="Number of reviews completed today")
