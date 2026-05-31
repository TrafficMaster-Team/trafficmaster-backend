from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReadPublicDecksRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    limit: int = Field(default=20, ge=1, le=100, title="Pagination", description="Limit for pagination")
    offset: int = Field(default=0, ge=0, title="Pagination", description="Offset for pagination")


class PublicDeckResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(title="Deck ID", description="Unique deck ID in system")
    owner_id: UUID = Field(title="Owner ID", description="The ID of the user who owns the deck")
    title: str = Field(title="Title", description="The deck title", examples=["Spanish verbs"])
    description: str | None = Field(default=None, title="Description", description="The deck description")
    created_at: datetime = Field(title="Created at", description="When the deck was created")
    updated_at: datetime = Field(title="Updated at", description="When the deck was last updated")


class ReadPublicDecksResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    decks: list[PublicDeckResponseSchema] = Field(default=[], title="Decks", description="The public decks")
