from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.card.errors.card import (
    TooLongAnswerError,
    TooLongAnswerOptionRationaleError,
    TooShortAnswerError,
)
from trafficmaster.domain.card.values.answer_option_id import AnswerOptionID
from trafficmaster.domain.common.entities.base_entity import BaseEntity

MIN_ANSWER_OPTION_TEXT: Final[int] = 1
MAX_ANSWER_OPTION_TEXT: Final[int] = 5000
MAX_ANSWER_OPTION_RATIONALE: Final[int] = 5000


@dataclass(eq=False)
class AnswerOption(BaseEntity[AnswerOptionID]):
    text: str
    is_correct: bool
    rationale: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self._validate()

    def _validate(self) -> None:
        if len(self.text) < MIN_ANSWER_OPTION_TEXT or self.text.isspace():
            msg = "Answer option text must be non-empty."
            raise TooShortAnswerError(msg)

        if len(self.text) > MAX_ANSWER_OPTION_TEXT:
            msg = f"Answer option text must be at most {MAX_ANSWER_OPTION_TEXT} characters long."
            raise TooLongAnswerError(msg)

        if len(self.rationale) > MAX_ANSWER_OPTION_RATIONALE:
            msg = f"Answer option rationale must be at most {MAX_ANSWER_OPTION_RATIONALE} characters long."
            raise TooLongAnswerOptionRationaleError(msg)

    @override
    def __str__(self) -> str:
        return self.text
