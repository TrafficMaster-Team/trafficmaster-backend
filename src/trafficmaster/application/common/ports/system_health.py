from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True, kw_only=True)
class SystemHealth:
    database_available: bool
    cache_available: bool

    @property
    def ready(self) -> bool:
        return self.database_available


class SystemHealthChecker(Protocol):
    async def check(self) -> SystemHealth: ...
