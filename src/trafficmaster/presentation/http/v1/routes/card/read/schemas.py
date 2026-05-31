from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReadCardResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(title="Card ID", description="Unique card ID in system")
    deck_id: UUID = Field(title="Deck ID", description="The ID of the deck the card belongs to")
    question: str = Field(title="Question", description="The card question", examples=["¿Cómo estás?"])
    answer: str = Field(title="Answer", description="The card answer", examples=["How are you?"])
    image_path: str | None = Field(default=None, title="Image path", description="Optional image path for the card")
    tags: list[str] | None = Field(default=None, title="Tags", description="The card tags")
