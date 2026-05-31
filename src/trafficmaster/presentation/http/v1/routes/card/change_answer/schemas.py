from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ChangeAnswerRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    answer: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Answer",
            description="The new card answer",
            examples=["How are you?"],
            min_length=1,
            max_length=5000,
        ),
    ]
