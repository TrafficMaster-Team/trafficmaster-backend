from dataclasses import dataclass
from typing import override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.deck.errors.deck import DeckTitleEmptyError


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class DeckTitle(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if self.value == "" or self.value.isspace():
            msg = "Title of deck cannot be empty"
            raise DeckTitleEmptyError(msg)

    @override
    def __str__(self) -> str:
        return self.value
