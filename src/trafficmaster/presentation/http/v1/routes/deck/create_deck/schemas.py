from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class CreateDeckRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    owner_id: UUID = Field(
        title="Owner ID",
        description="The ID of the user who will own the deck",
        examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
    )
    deck_config_id: UUID = Field(
        title="Deck Config ID",
        description="The ID of the deck config to attach to the deck",
        examples=["75079971-fb0e-4e04-bf07-ceb57faebe84"],
    )
    title: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(title="Title", description="The deck title", examples=["Spanish verbs"], min_length=1, max_length=255),
    ]
    description: Annotated[
        str | None,
        Field(title="Description", description="The deck description", examples=["Irregular verbs"]),
    ] = None
    is_public: Annotated[
        bool,
        Field(title="Is public", description="Whether the deck is publicly visible"),
    ] = False


class CreateDeckResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(
        title="Deck ID",
        description="Unique deck ID in system. Here we store in UUID",
        examples=["75079971-fb0e-4e04-bf07-ceb57faebe84"],
    )
