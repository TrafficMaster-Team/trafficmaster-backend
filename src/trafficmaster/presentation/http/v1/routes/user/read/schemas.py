from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ReadUserByIDResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(
        title="User ID",
        description="Unique user ID in system. Here we store in UUID",
        examples=[
            "75079971-fb0e-4e04-bf07-ceb57faebe84",
            "19178bf6-8f84-406e-b213-102ec84fab9f",
        ],
    )

    email: EmailStr = Field(
        title="User Email",
        description="User email in system. Email must be unique",
        examples=["tiji-hiyosi44@mail.ru", "xapamih_eni98@gmail.com"],
    )

    name: str = Field(
        title="User Name",
        description="User name that was provided during registration",
        examples=[
            "Svetlana",
            "Vladislav",
            "Lolita",
        ],
    )

    role: Literal["admin", "user", "super_admin"] = Field(
        title="User Role",
        description="User role in system",
        examples=["admin", "user", "super_admin"],
    )
