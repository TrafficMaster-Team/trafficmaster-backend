from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


class ChangeUserEmailRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: Annotated[
        EmailStr,
        BeforeValidator(lambda x: str.strip(str(x))),
        Field(title="User Email", description="The user email address", examples=["supir_edge2008@gmail.com"]),
    ]
