from datetime import UTC, datetime
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import (
    create_password_hash,
    create_user_email,
    create_user_id,
    create_username,
)
from trafficmaster.domain.common.errors import DomainError
from trafficmaster.domain.user.entities.user import SerializedUser, User
from trafficmaster.domain.user.values.user_role import UserRole


def test_creates_user_with_defaults() -> None:
    # Arrange
    user_id = create_user_id()
    email = create_user_email()
    username = create_username()
    password_hash = create_password_hash()

    # Act
    sut = User(
        id=user_id,
        email=email,
        name=username,
        hashed_password=password_hash,
    )

    # Assert
    assert sut.id == user_id
    assert sut.email == email
    assert sut.name == username
    assert sut.hashed_password == password_hash
    assert sut.role == UserRole.USER
    assert sut.is_active is True


def test_creates_user_with_explicit_values() -> None:
    # Arrange
    user_id = create_user_id()
    email = create_user_email("bob@example.com")
    username = create_username("Bob")
    password_hash = create_password_hash(b"custom_hash")
    role = UserRole.ADMIN
    is_active = False

    # Act
    sut = User(
        id=user_id,
        email=email,
        name=username,
        hashed_password=password_hash,
        role=role,
        is_active=is_active,
    )

    # Assert
    assert sut.id == user_id
    assert sut.email == email
    assert sut.name == username
    assert sut.hashed_password == password_hash
    assert sut.role == role
    assert sut.is_active == is_active


@pytest.mark.parametrize(
    "role",
    [UserRole.USER, UserRole.ADMIN, UserRole.SUPERADMIN],
)
def test_user_can_have_different_roles(role: UserRole) -> None:
    # Arrange
    user_id = create_user_id()
    email = create_user_email()
    username = create_username()
    password_hash = create_password_hash()

    # Act
    sut = User(
        id=user_id,
        email=email,
        name=username,
        hashed_password=password_hash,
        role=role,
    )

    # Assert
    assert sut.role == role


def test_same_id_users_are_equal() -> None:
    # Arrange
    same_id = create_user_id()
    user1 = create_user(user_id=same_id, username=create_username("Alice"))
    user2 = create_user(user_id=same_id, username=create_username("Bob"))

    # Assert
    assert user1 == user2
    assert hash(user1) == hash(user2)


def test_different_id_users_are_not_equal() -> None:
    # Arrange
    user1 = create_user(user_id=create_user_id())
    user2 = create_user(user_id=create_user_id())

    # Assert
    assert user1 != user2


def test_user_is_not_equal_to_other_type() -> None:
    # Arrange
    sut = create_user()

    # Assert
    assert sut != "not a user"


def test_user_can_be_mutated_except_id() -> None:
    # Arrange
    sut = create_user()
    new_email = create_user_email("newemail@example.com")
    new_username = create_username("NewName")
    new_password_hash = create_password_hash(b"new_hash")
    new_role = UserRole.ADMIN
    new_is_active = False

    # Act
    sut.email = new_email
    sut.name = new_username
    sut.hashed_password = new_password_hash
    sut.role = new_role
    sut.is_active = new_is_active

    # Assert
    assert sut.email == new_email
    assert sut.name == new_username
    assert sut.hashed_password == new_password_hash
    assert sut.role == new_role
    assert sut.is_active == new_is_active


def test_user_id_cannot_be_changed() -> None:
    # Arrange
    sut = create_user()

    # Act & Assert
    with pytest.raises(DomainError):
        sut.id = create_user_id()


def test_user_serialize() -> None:
    # Arrange
    user_id = create_user_id()
    email = create_user_email("alice@example.com")
    username = create_username("Alice")
    password_hash = create_password_hash(b"hash123")
    role = UserRole.ADMIN
    is_active = False

    sut = User(
        id=user_id,
        email=email,
        name=username,
        hashed_password=password_hash,
        role=role,
        is_active=is_active,
    )

    # Act
    result = sut.serialize()

    # Assert
    assert isinstance(result, dict)
    assert result["id"] == str(user_id)
    assert result["email"] == str(email)
    assert result["name"] == str(username)
    assert result["role"] == role.value
    assert result["is_active"] == is_active
    assert result["password"] == password_hash.password.decode("utf-8")
    assert result["created_at"] == sut.created_at.isoformat()
    assert result["updated_at"] == sut.updated_at.isoformat()


def test_user_deserialize() -> None:
    # Arrange
    user_id = uuid4()
    email = "bob@example.com"
    username = "Bob"
    stored_hash = "hash456"
    role = UserRole.USER
    is_active = True
    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)

    serialized_data: SerializedUser = {
        "id": str(user_id),
        "email": email,
        "name": username,
        "role": role.value,
        "is_active": is_active,
        "password": stored_hash,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
    }

    # Act
    sut = User.deserialize(serialized_data)

    # Assert
    assert sut.id == user_id
    assert str(sut.email) == email
    assert str(sut.name) == username
    assert sut.role == role
    assert sut.is_active == is_active
    assert sut.hashed_password.password == stored_hash.encode("utf-8")
    assert sut.created_at == created_at
    assert sut.updated_at == updated_at


def test_user_serialize_deserialize_roundtrip() -> None:
    # Arrange
    original = create_user(
        email=create_user_email("test@example.com"),
        username=create_username("TestUser"),
        role=UserRole.ADMIN,
        is_active=False,
    )

    # Act
    serialized = original.serialize()
    deserialized = User.deserialize(serialized)

    # Assert
    assert deserialized.id == original.id
    assert deserialized.email == original.email
    assert deserialized.name == original.name
    assert deserialized.role == original.role
    assert deserialized.is_active == original.is_active
    assert deserialized.hashed_password == original.hashed_password
    assert deserialized.created_at == original.created_at
    assert deserialized.updated_at == original.updated_at


def test_user_can_be_used_in_set() -> None:
    # Arrange
    same_id = create_user_id()
    user1 = create_user(user_id=same_id, username=create_username("Alice"))
    user2 = create_user(user_id=same_id, username=create_username("Bob"))
    user3 = create_user(user_id=create_user_id(), username=create_username("Charlie"))

    # Act
    user_set = {user1, user2, user3}

    # Assert
    assert len(user_set) == 2
    assert user1 in user_set
    assert user2 in user_set
    assert user3 in user_set
