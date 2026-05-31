from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ChangeConfigNameRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(title="Name", description="The new deck config name", examples=["Default"], min_length=1, max_length=255),
    ]
