from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from trafficmaster.domain.common.errors import DomainError, InconsistentTimeError


@dataclass(eq=False, kw_only=True)
class BaseEntity[OIDType]:
    id: OIDType

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.updated_at < self.created_at:
            msg = (
                f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}"
                f" cannot be earlier than"
                f" {self.created_at.strftime('%Y-%m-%dT%H:%M:%S')}"
            )
            raise InconsistentTimeError(msg)

    def __setattr__(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Denying access to set ID parameter"""

        if key == "id" and getattr(self, "id", None) is not None:
            msg = "Changing of ID parameter is not permitted."
            raise DomainError(msg)

        super().__setattr__(key, value)

    def __eq__(self, other: object) -> bool:

        if other is None:
            return False

        if type(self) is not type(other):
            return False

        if isinstance(other, BaseEntity):
            return bool(self.id == other.id)

        return False

    def __hash__(self) -> int:
        return hash((type(self), self.id))
