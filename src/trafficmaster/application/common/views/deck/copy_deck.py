from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CopyDeckView:
    deck_id: UUID
    deck_config_id: UUID
