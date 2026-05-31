from pydantic import BaseModel, ConfigDict, Field


class ReadUserAggregateStatsResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_decks: int = Field(title="Total decks", description="Total number of decks owned by the user", examples=[12])
    total_cards: int = Field(title="Total cards", description="Total number of cards owned by the user", examples=[340])
    new_count: int = Field(title="New cards", description="Number of cards in the NEW state", examples=[50])
    learning_count: int = Field(
        title="Learning cards",
        description="Number of cards in the LEARNING or RELEARNING state",
        examples=[20],
    )
    review_count: int = Field(title="Review cards", description="Number of cards in the REVIEW state", examples=[270])
    due_learning: int = Field(title="Due learning", description="Number of learning cards due now", examples=[5])
    due_review: int = Field(title="Due review", description="Number of review cards due now", examples=[18])
    new_done_today: int = Field(title="New done today", description="Number of new cards studied today", examples=[10])
    reviews_done_today: int = Field(
        title="Reviews done today",
        description="Number of reviews completed today",
        examples=[42],
    )
