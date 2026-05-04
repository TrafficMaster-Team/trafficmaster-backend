from datetime import datetime, timedelta
from typing import Protocol


class SessionTimer(Protocol):
    @property
    def refresh_trigger_interval(self) -> timedelta: ...

    @property
    def current_time(self) -> datetime: ...

    @property
    def auth_session_expired(self) -> datetime: ...
