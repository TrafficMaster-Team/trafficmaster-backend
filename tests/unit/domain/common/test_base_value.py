from dataclasses import FrozenInstanceError

import pytest

from tests.unit.domain.factories.value_object import (
    EmptyValue,
    IntValue,
    PositiveValue,
    SuperStrValue,
    SuperValidateValue,
)
from trafficmaster.domain.common.errors import DomainFieldError


def test_value_objects_with_same_value_are_equal() -> None:
    assert IntValue(value=1) == IntValue(value=1)


def test_value_objects_with_different_value_are_not_equal() -> None:
    assert IntValue(value=1) != IntValue(value=2)


def test_equal_value_objects_have_equal_hash() -> None:
    assert hash(IntValue(value=1)) == hash(IntValue(value=1))


def test_value_object_can_be_used_in_set() -> None:
    values = {IntValue(value=1), IntValue(value=1), IntValue(value=2)}

    assert len(values) == 2


def test_value_object_is_immutable() -> None:
    sut = IntValue(value=1)

    with pytest.raises(FrozenInstanceError):
        sut.value = 2


def test_validate_is_called_on_construction() -> None:
    with pytest.raises(DomainFieldError):
        PositiveValue(value=-1)


def test_value_object_passes_validation_with_valid_value() -> None:
    sut = PositiveValue(value=1)

    assert sut.value == 1


def test_value_object_without_fields_raises() -> None:
    with pytest.raises(DomainFieldError):
        EmptyValue()


def test_base_validate_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        SuperValidateValue(value=1)


def test_base_str_raises_not_implemented() -> None:
    sut = SuperStrValue(value=1)

    with pytest.raises(NotImplementedError):
        str(sut)
