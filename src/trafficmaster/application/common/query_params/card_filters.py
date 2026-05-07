from dataclasses import dataclass
from enum import StrEnum

from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.query_params.user_filters import UserQueryFilters
from trafficmaster.domain.deck.values.deck_id import DeckID


class CardQueryFilters(StrEnum):
    question = "question"
    created_at = "created_at"
    updated_at = "updated_at"


@dataclass(frozen=True, kw_only=True, slots=True)
class CardParams:
    pagination: Pagination
    sorting_order: SortingOrder
    sorting_filter: UserQueryFilters
    deck_id: DeckID | None = None
    tags: tuple[str] | None = None
