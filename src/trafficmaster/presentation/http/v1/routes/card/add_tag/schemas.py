from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class AddTagRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    tag: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(title="Tag", description="The tag to add to the card", examples=["grammar"], min_length=1, max_length=50),
    ]
