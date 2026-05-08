from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    @property
    def current_time(self) -> datetime: ...

    @property
    def today_start(self) -> datetime: ...
