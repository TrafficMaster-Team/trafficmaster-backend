from abc import abstractmethod
from typing import Protocol


class AuthIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> str: ...
