from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.presentation.http.v1.routes.deck_config.read.schemas import ReadDeckConfigResponseSchema


class ReadUserDeckConfigsResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    configs: list[ReadDeckConfigResponseSchema] = Field(
        default=[],
        title="Deck configs",
        description="The deck configs owned by the user",
    )
