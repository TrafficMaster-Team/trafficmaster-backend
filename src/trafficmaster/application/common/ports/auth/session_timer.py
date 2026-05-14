from datetime import datetime, timedelta
from typing import Protocol


class SessionTimer(Protocol):
    @property
    def refresh_trigger_interval(self) -> timedelta: ...

    @property
    def auth_session_expires_at(self) -> datetime: ...
