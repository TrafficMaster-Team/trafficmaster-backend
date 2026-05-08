from datetime import UTC, datetime, time


class UtcClock:
    @property
    def current_time(self) -> datetime:
        return datetime.now(UTC)

    @property
    def today_start(self) -> datetime:
        return datetime.combine(self.current_time.date(), time.min, tzinfo=UTC)
