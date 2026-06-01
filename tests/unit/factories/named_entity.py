from dataclasses import dataclass

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.common.values.base_value import BaseValueObject


@dataclass(frozen=True, slots=True, repr=False)
class NamedEntityID(BaseValueObject):
    value: int

    def _validate(self) -> None: ...

    def __str__(self) -> str:
        return str(self.value)


class NamedEntity(BaseEntity[NamedEntityID]):
    def __init__(self, id_: NamedEntityID, name: str) -> None:
        super().__init__(id=id_)
        self.name = name


class NamedEntitySubclass(NamedEntity):
    def __init__(self, id_: NamedEntityID, name: str, value: int) -> None:
        super().__init__(id_=id_, name=name)
        self.value = value


def create_entity_id(id_: int = 42) -> NamedEntityID:
    return NamedEntityID(value=id_)


def create_named_entity(id_: int = 42, name: str = "name") -> NamedEntity:
    return NamedEntity(id_=NamedEntityID(value=id_), name=name)


def create_named_entity_subclass(
    id_: int = 42,
    name: str = "name",
    value: int = 314,
) -> NamedEntitySubclass:
    return NamedEntitySubclass(id_=NamedEntityID(id_), name=name, value=value)
