from dataclasses import dataclass

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.common.values.base_value import BaseValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TaggedEntityID(BaseValueObject):
    value: int

    def __str__(self) -> str: ...

    def _validate(self) -> None: ...


class TaggedEntity(BaseEntity[TaggedEntityID]):
    def __init__(self, *, id_: TaggedEntityID, tag: str) -> None:
        super().__init__(id=id_)
        self._tag = tag


def create_tagged_entity_id(id_: int = 54) -> TaggedEntityID:
    return TaggedEntityID(value=id_)


def create_tagged_entity(id_: int = 54, tag: str = "tag") -> TaggedEntity:
    return TaggedEntity(id_=id_, tag=tag)
