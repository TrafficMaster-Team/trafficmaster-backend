from dataclasses import dataclass

from trafficmaster.application.errors.query_params import PaginationError


@dataclass(slots=True, frozen=True, kw_only=True)
class Pagination:
    limit: int | None = None
    offset: int | None = None

    def __post_init__(self) -> None:
        msg: str | None
        if self.offset is not None and self.offset < 0:
            msg = f"offset must be non-negative: {self.offset}"
            raise PaginationError(msg)
        if self.limit is not None and self.limit < 0:
            msg = f"limit must be non-negative: {self.limit}"
            raise PaginationError(msg)
