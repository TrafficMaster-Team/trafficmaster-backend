from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChangeCardDeckRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    deck_id: UUID = Field(
        title="Deck ID",
        description="The ID of the deck to move the card to",
        examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
    )
