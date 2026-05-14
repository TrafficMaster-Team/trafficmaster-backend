from typing import Protocol


class AuthIDGenerator(Protocol):
    def __call__(self) -> str: ...
