from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ChangeUsernameRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    username: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Username",
            description="The username to change",
            examples=["sinsha1231"],
            min_length=5,
            max_length=30,
        ),
    ]
