from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadDeckByIDView:
    id: UUID
    owner_id: UUID
    deck_config_id: UUID
    title: str
    description: str | None
    is_public: bool
