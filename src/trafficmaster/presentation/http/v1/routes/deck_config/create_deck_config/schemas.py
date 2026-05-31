from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from trafficmaster.presentation.http.v1.routes.deck_config.shared_schemas import (
    AdvancedConfigSchema,
    DailyLimitsSchema,
    LapsesConfigSchema,
    NewCardsConfigSchema,
)


class CreateDeckConfigRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    owner_id: UUID = Field(
        title="Owner ID",
        description="The ID of the user who will own the deck config",
        examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
    )
    name: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(title="Name", description="The deck config name", examples=["Default"], min_length=1, max_length=255),
    ]
    daily_limits: DailyLimitsSchema = Field(default_factory=DailyLimitsSchema, title="Daily limits")
    new_cards: NewCardsConfigSchema = Field(title="New cards config")
    lapses: LapsesConfigSchema = Field(title="Lapses config")
    advanced: AdvancedConfigSchema = Field(title="Advanced config")


class CreateDeckConfigResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(
        title="Deck Config ID",
        description="Unique deck config ID in system. Here we store in UUID",
        examples=["75079971-fb0e-4e04-bf07-ceb57faebe84"],
    )
