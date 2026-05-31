from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ChangeTitleRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Title", description="The new deck title", examples=["Spanish verbs"], min_length=1, max_length=255
        ),
    ]
