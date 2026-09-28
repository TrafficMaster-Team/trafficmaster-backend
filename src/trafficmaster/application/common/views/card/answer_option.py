from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class AnswerOptionView:
    id: UUID
    text: str
    is_correct: bool
    rationale: str
