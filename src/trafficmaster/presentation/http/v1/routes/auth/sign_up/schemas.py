from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


class SignUpRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: Annotated[
        EmailStr,
        BeforeValidator(lambda x: str.strip(str(x))),
        Field(title="User Email", description="The user email address", examples=["supir_edge2008@gmail.com"]),
    ]
    name: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Username",
            description="The username to register with",
            examples=["sinsha1231"],
            min_length=5,
            max_length=30,
        ),
    ]
    password: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Password",
            description="The password to register with",
            examples=["s3cr3t_p4ssw0rd"],
            min_length=8,
            max_length=255,
        ),
    ]


class SignUpResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(
        title="User ID",
        description="Unique user ID in system. Here we store in UUID",
        examples=[
            "75079971-fb0e-4e04-bf07-ceb57faebe84",
            "19178bf6-8f84-406e-b213-102ec84fab9f",
        ],
    )
