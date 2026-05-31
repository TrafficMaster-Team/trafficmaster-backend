from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ChangeQuestionRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Question",
            description="The new card question",
            examples=["¿Cómo estás?"],
            min_length=1,
            max_length=500,
        ),
    ]
