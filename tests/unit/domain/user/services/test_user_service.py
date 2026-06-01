from unittest.mock import Mock

import pytest

from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import (
    create_password_hash,
    create_raw_password,
    create_user_email,
    create_user_id,
    create_username,
)
from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.errors.user import RoleAssignmentNotPermittedError
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.user_role import UserRole


@pytest.mark.parametrize(
    "role",
    [UserRole.USER, UserRole.ADMIN],
)
def test_creates_active_user_with_hashed_password(
    role: UserRole,
    id_generator: Mock,
    password_hasher: Mock,
) -> None:
    # Arrange
    email = create_user_email()
    username = create_username()
    raw_password = create_raw_password()

    expected_id = create_user_id()
    expected_hash = create_password_hash()

    id_generator.return_value = expected_id
    password_hasher.hash_password.return_value = expected_hash
    sut = UserService(id_generator=id_generator, password_hasher=password_hasher)

    # Act
    result = sut.create_user(name=username, email=email, raw_password=raw_password, role=role)

    # Assert
    assert isinstance(result, User)
    assert result.id == expected_id
    assert result.email == email
    assert result.name == username
    assert result.hashed_password == expected_hash
    assert result.role == role
    assert result.is_active is True
    password_hasher.hash_password.assert_called_once_with(password=raw_password)


def test_fails_to_create_user_with_unassignable_role(
    id_generator: Mock,
    password_hasher: Mock,
) -> None:
    # Arrange
    sut = UserService(id_generator=id_generator, password_hasher=password_hasher)

    # Act & Assert
    with pytest.raises(RoleAssignmentNotPermittedError):
        sut.create_user(
            name=create_username(),
            email=create_user_email(),
            raw_password=create_raw_password(),
            role=UserRole.SUPERADMIN,
        )


@pytest.mark.parametrize(
    "is_valid",
    [True, False],
)
def test_verifies_password(
    is_valid: bool,
    id_generator: Mock,
    password_hasher: Mock,
) -> None:
    # Arrange
    user = create_user()
    raw_password = create_raw_password()

    password_hasher.verify_password.return_value = is_valid
    sut = UserService(id_generator=id_generator, password_hasher=password_hasher)

    # Act
    result = sut.verify_password(user, raw_password)

    # Assert
    assert result is is_valid
    password_hasher.verify_password.assert_called_once_with(
        raw_password=raw_password,
        hashed_password=user.hashed_password,
    )


def test_changes_password(
    id_generator: Mock,
    password_hasher: Mock,
) -> None:
    # Arrange
    user = create_user(password_hash=create_password_hash(b"old"))
    expected_hash = create_password_hash(b"new")
    password_hasher.hash_password.return_value = expected_hash
    sut = UserService(id_generator=id_generator, password_hasher=password_hasher)

    # Act
    sut.change_password(user, create_raw_password())

    # Assert
    assert user.hashed_password == expected_hash


def test_changes_email(
    id_generator: Mock,
    password_hasher: Mock,
) -> None:
    # Arrange
    user = create_user()
    new_email = create_user_email("changed@example.com")
    sut = UserService(id_generator=id_generator, password_hasher=password_hasher)

    # Act
    sut.change_email(user, new_email)

    # Assert
    assert user.email == new_email


def test_changes_name(
    id_generator: Mock,
    password_hasher: Mock,
) -> None:
    # Arrange
    user = create_user()
    new_name = create_username("NewName")
    sut = UserService(id_generator=id_generator, password_hasher=password_hasher)

    # Act
    sut.change_name(user, new_name)

    # Assert
    assert user.name == new_name
