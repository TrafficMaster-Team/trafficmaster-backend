from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from trafficmaster.presentation.http.v1.routes.card.create_card.schemas import AnswerOptionSchema


class ChangeCardContentRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    answer_options: list[AnswerOptionSchema] = Field(alias="answerOptions", min_length=1)
    hint: Annotated[
        str,
        BeforeValidator(lambda x: x.strip()),
        Field(
            title="Hint",
            description="The new card hint",
            max_length=5000,
        ),
    ]
