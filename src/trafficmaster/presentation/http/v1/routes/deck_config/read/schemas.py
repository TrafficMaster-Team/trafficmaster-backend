from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.presentation.http.v1.routes.deck_config.shared_schemas import (
    AdvancedConfigSchema,
    DailyLimitsSchema,
    LapsesConfigSchema,
    NewCardsConfigSchema,
)


class ReadDeckConfigResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    id: UUID = Field(title="Deck Config ID", description="Unique deck config ID in system")
    owner_id: UUID = Field(title="Owner ID", description="The ID of the user who owns the deck config")
    name: str = Field(title="Name", description="The deck config name", examples=["Default"])
    daily_limits: DailyLimitsSchema = Field(title="Daily limits")
    new_cards: NewCardsConfigSchema = Field(title="New cards config")
    lapses: LapsesConfigSchema = Field(title="Lapses config")
    advanced: AdvancedConfigSchema = Field(title="Advanced config")
