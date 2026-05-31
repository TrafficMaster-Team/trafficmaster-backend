from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ChangeImagePathRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    image_path: Annotated[
        str | None,
        Field(
            title="Image path",
            description="The new image path for the card. Pass null to remove the image",
            examples=["images/card-123.png"],
        ),
    ] = None
