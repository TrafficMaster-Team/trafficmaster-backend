from dataclasses import dataclass
from enum import StrEnum

from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.common.query_params.sorting import SortingOrder


class UserQueryFilters(StrEnum):
    name = "name"
    email = "email"
    role = "role"
    id = "id"


@dataclass(frozen=True, slots=True, kw_only=True)
class UserParams:
    pagination: Pagination
    sorting_order: SortingOrder
    sorting_filter: UserQueryFilters
