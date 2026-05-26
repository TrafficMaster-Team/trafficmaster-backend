from typing import Protocol

from trafficmaster.infrastructure.errors.base import InfrastructureError


class CacheStoreError(InfrastructureError):
    """Raised by CacheStore implementations on backend failure (network, protocol, etc.)."""


class CacheStore(Protocol):
    async def set(self, name: str, value: bytes, ttl: int) -> None: ...

    async def get(self, name: str) -> bytes | None: ...

    async def delete(self, name: str) -> None: ...
