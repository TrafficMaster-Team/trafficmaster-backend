from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CopyDeckResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    deck_id: UUID = Field(title="Deck ID", description="The ID of the newly copied deck")
    deck_config_id: UUID = Field(title="Deck Config ID", description="The ID of the newly copied deck config")
