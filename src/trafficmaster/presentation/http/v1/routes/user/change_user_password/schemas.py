from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ChangeUserPasswordRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    password: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Password",
            description="The new user password",
            examples=["s3cr3t_p4ssw0rd"],
            min_length=8,
            max_length=255,
        ),
    ]
