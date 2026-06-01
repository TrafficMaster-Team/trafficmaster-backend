from datetime import UTC, datetime

import pytest

from tests.unit.domain.factories.named_entity import create_entity_id, create_named_entity, create_named_entity_subclass
from tests.unit.domain.factories.tagged_entity import create_tagged_entity
from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.common.errors import DomainError, InconsistentTimeError


@pytest.mark.parametrize("new_id", [pytest.param(1, id="same_id"), pytest.param(1000, id="different_id")])
def test_entity_id_cannot_be_changed(new_id: int) -> None:
    sut = create_named_entity()

    with pytest.raises(DomainError):
        sut.id = create_entity_id(new_id)


def test_entity_is_mutable_except_id() -> None:
    sut = create_named_entity(name="Boss")

    new_name = "NewBoss"

    sut.name = new_name

    assert sut.name == new_name


@pytest.mark.parametrize(
    ("name1", "name2"),
    [
        pytest.param("Denis", "Denis", id="same_name"),
        pytest.param("Denis", "neDenis", id="different_name"),
    ],
)
def test_same_type_entities_with_same_id_are_equal(name1: str, name2: str) -> None:
    e1 = create_named_entity(name=name1)
    e2 = create_named_entity(name=name2)

    assert e1 == e2


def test_same_type_entities_with_different_id_are_not_equal() -> None:
    e1 = create_named_entity(id_=1)
    e2 = create_named_entity(id_=2)

    assert e1 != e2


def test_different_type_entities_with_same_id_are_not_equal() -> None:
    e1 = create_named_entity(id_=1)
    e2 = create_tagged_entity(id_=1)

    assert e1 != e2


def test_entity_is_not_equal_to_subclass_with_same_id() -> None:
    parent = create_named_entity()
    child = create_named_entity_subclass(id_=parent.id.value, name=parent.name, value=1)

    assert parent.__eq__(child) is False
    assert child.__eq__(parent) is False


def test_equal_entities_have_equal_hash() -> None:
    sut_id = 1
    e1 = create_named_entity(sut_id, name="Bob")
    e2 = create_named_entity(sut_id, name="neBob")

    assert e1 == e2
    assert hash(e1) == hash(e2)


def test_entity_can_be_used_in_set() -> None:
    e1 = create_named_entity()
    e2 = create_named_entity(id_=2, name="Alice")
    e3 = create_named_entity(id_=2, name="Bob")
    e4 = create_tagged_entity()

    entity_set = {e1, e2, e3, e4}

    assert len(entity_set) == 3


def test_entity_is_not_equal_to_none() -> None:
    sut = create_named_entity()

    assert sut.__eq__(None) is False


def test_entity_is_not_equal_to_non_entity_object() -> None:
    sut = create_named_entity()

    assert sut.__eq__("not-an-entity") is False


def test_entity_with_updated_at_before_created_at_raises() -> None:
    created_at = datetime(2026, 1, 2, tzinfo=UTC)
    updated_at = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(InconsistentTimeError):
        BaseEntity(id=create_entity_id(), created_at=created_at, updated_at=updated_at)


def test_entity_with_consistent_timestamps_is_created() -> None:
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    updated_at = datetime(2026, 1, 2, tzinfo=UTC)

    sut = BaseEntity(id=create_entity_id(), created_at=created_at, updated_at=updated_at)

    assert sut.created_at == created_at
    assert sut.updated_at == updated_at
