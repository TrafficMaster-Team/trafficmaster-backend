from datetime import UTC, datetime, timedelta


class UtcAuthSessionTimer:
    def __init__(self, ttl: timedelta, refresh_threshold: float) -> None:
        self._ttl = ttl
        self._refresh_threshold = refresh_threshold

    @property
    def current_time(self) -> datetime:
        return datetime.now(UTC)

    @property
    def auth_session_expired(self) -> datetime:
        return self.current_time + self._ttl

    @property
    def refresh_trigger_interval(self) -> timedelta:
        return self._ttl * self._refresh_threshold
