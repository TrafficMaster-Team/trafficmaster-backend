from dataclasses import dataclass
from typing import override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck_config import DeckConfigNameEmptyError


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class DeckConfigName(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if self.value == "" or self.value.isspace():
            msg = "Name of config deck cannot be empty"
            raise DeckConfigNameEmptyError(msg)

    @override
    def __str__(self) -> str:
        return self.value
