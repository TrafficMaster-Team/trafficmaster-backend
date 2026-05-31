from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.presentation.http.v1.routes.deck.read.schemas import ReadDeckResponseSchema


class ReadUserDecksResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    decks: list[ReadDeckResponseSchema] = Field(
        default=[],
        title="Decks",
        description="The decks owned by the user",
    )
