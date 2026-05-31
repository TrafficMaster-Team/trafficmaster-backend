from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ChangeDescriptionRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    description: Annotated[
        str | None,
        Field(title="Description", description="The new deck description", examples=["Irregular verbs"]),
    ] = None
