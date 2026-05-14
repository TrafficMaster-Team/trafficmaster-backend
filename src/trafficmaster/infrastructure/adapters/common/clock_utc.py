from datetime import UTC, datetime


class UtcClock:
    @property
    def current_time(self) -> datetime:
        return datetime.now(UTC)

    @property
    def today_start(self) -> datetime:
        return self.current_time.replace(hour=0, minute=0, second=0, microsecond=0)
