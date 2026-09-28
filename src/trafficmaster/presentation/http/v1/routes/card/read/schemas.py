from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.presentation.http.v1.routes.card.create_card.schemas import AnswerOptionResponseSchema


class ReadCardResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    id: UUID = Field(title="Card ID", description="Unique card ID in system")
    deck_id: UUID = Field(title="Deck ID", description="The ID of the deck the card belongs to")
    question: str = Field(title="Question", description="The card question", examples=["¿Cómo estás?"])
    answer_options: list[AnswerOptionResponseSchema] = Field(
        alias="answerOptions", title="Answer options", description="Possible card answers"
    )
    hint: str = Field(title="Hint", description="The card hint")
    image_path: str | None = Field(default=None, title="Image path", description="Optional image path for the card")
    tags: list[str] | None = Field(default=None, title="Tags", description="The card tags")
