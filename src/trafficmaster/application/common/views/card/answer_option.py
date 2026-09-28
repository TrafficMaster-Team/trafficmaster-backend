from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AnswerOptionView:
    text: str
    is_correct: bool
    rationale: str
