from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class CreateCardRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    deck_id: UUID = Field(
        title="Deck ID",
        description="The ID of the deck the card belongs to",
        examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
    )
    question: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Question", description="The card question", examples=["¿Cómo estás?"], min_length=1, max_length=500
        ),
    ]
    answer: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(title="Answer", description="The card answer", examples=["How are you?"], min_length=1, max_length=5000),
    ]
    tags: Annotated[
        list[str] | None,
        Field(title="Tags", description="The card tags", examples=[["greetings", "basic"]]),
    ] = None


class CreateCardResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(
        title="Card ID",
        description="Unique card ID in system. Here we store in UUID",
        examples=["75079971-fb0e-4e04-bf07-ceb57faebe84"],
    )
