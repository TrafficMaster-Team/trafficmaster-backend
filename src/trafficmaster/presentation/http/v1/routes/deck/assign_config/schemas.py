from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssignDeckConfigRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    deck_config_id: UUID = Field(
        title="Deck Config ID",
        description="The ID of the deck config to assign to the deck",
        examples=["75079971-fb0e-4e04-bf07-ceb57faebe84"],
    )
