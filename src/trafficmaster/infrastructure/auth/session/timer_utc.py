from datetime import datetime, timedelta
from typing import Final

from trafficmaster.application.common.ports.clock import Clock


class UtcAuthSessionTimer:
    def __init__(self, clock: Clock, ttl: timedelta, refresh_threshold: float) -> None:
        self._clock: Final[Clock] = clock
        self._ttl: Final[timedelta] = ttl
        self._refresh_threshold: Final[float] = refresh_threshold

    @property
    def auth_session_expires_at(self) -> datetime:
        return self._clock.current_time + self._ttl

    @property
    def refresh_trigger_interval(self) -> timedelta:
        return self._ttl * self._refresh_threshold
