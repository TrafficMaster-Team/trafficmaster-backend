from datetime import UTC, datetime
from typing import override

from trafficmaster.application.common.ports.clock import Clock


class UtcClock(Clock):
    @property
    @override
    def current_time(self) -> datetime:
        return datetime.now(UTC)

    @property
    @override
    def today_start(self) -> datetime:
        return self.current_time.replace(hour=0, minute=0, second=0, microsecond=0)
