from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


class LogInRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: Annotated[
        EmailStr,
        BeforeValidator(lambda x: str.strip(str(x))),
        Field(title="User Email", description="The user email address", examples=["supir_edge2008@gmail.com"]),
    ]
    password: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(title="Password", description="The user password", examples=["s3cr3t_p4ssw0rd"]),
    ]
