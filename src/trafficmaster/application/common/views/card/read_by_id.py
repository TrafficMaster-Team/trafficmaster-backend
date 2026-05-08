from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadCardByIDView:
    id: UUID
    deck_id: UUID
    question: str
    answer: str
    image_path: str | None
    tags: list[str] | None
