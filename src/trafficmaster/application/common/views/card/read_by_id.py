from dataclasses import dataclass
from uuid import UUID

from trafficmaster.application.common.views.card.answer_option import AnswerOptionView


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadCardByIDView:
    id: UUID
    deck_id: UUID
    question: str
    answer_options: list[AnswerOptionView]
    hint: str
    image_path: str | None
    tags: list[str] | None
