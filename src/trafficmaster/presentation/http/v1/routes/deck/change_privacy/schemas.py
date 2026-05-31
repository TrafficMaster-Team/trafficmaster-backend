from pydantic import BaseModel, ConfigDict, Field


class ChangePrivacyRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    is_public: bool = Field(title="Is public", description="Whether the deck is publicly visible")
