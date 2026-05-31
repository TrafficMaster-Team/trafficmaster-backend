from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReadDeckResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(title="Deck ID", description="Unique deck ID in system")
    owner_id: UUID = Field(title="Owner ID", description="The ID of the user who owns the deck")
    deck_config_id: UUID = Field(title="Deck Config ID", description="The ID of the attached deck config")
    title: str = Field(title="Title", description="The deck title", examples=["Spanish verbs"])
    description: str | None = Field(
        default=None,
        title="Description",
        description="The deck description",
        examples=["Irregular verbs"],
    )
    is_public: bool = Field(title="Is public", description="Whether the deck is publicly visible")
