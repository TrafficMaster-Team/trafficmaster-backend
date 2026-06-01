import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.domain.user.errors.user import (
    AccessChangeNotPermittedError,
    RoleChangeNotPermittedError,
)
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_role import UserRole


@pytest.mark.parametrize(
    ("initial_role", "is_admin", "expected_role"),
    [
        pytest.param(UserRole.USER, True, UserRole.ADMIN, id="user_to_admin"),
        pytest.param(UserRole.ADMIN, False, UserRole.USER, id="admin_to_user"),
    ],
)
def test_toggles_admin_role(initial_role: UserRole, is_admin: bool, expected_role: UserRole) -> None:
    # Arrange
    user = create_user(role=initial_role)
    sut = AccessService()

    # Act
    sut.toggle_admin_role(user, is_admin=is_admin)

    # Assert
    assert user.role == expected_role


@pytest.mark.parametrize("is_admin", [True, False])
def test_cannot_toggle_superadmin_role(is_admin: bool) -> None:
    # Arrange
    user = create_user(role=UserRole.SUPERADMIN)
    sut = AccessService()

    # Act & Assert
    with pytest.raises(RoleChangeNotPermittedError):
        sut.toggle_admin_role(user, is_admin=is_admin)

    assert user.role == UserRole.SUPERADMIN


@pytest.mark.parametrize(
    ("initial_state", "target_state"),
    [
        pytest.param(True, False, id="active_to_inactive"),
        pytest.param(False, True, id="inactive_to_active"),
    ],
)
def test_toggles_user_activation(initial_state: bool, target_state: bool) -> None:
    # Arrange
    user = create_user(is_active=initial_state)
    sut = AccessService()

    # Act
    sut.toggle_user_activation(user, is_active=target_state)

    # Assert
    assert user.is_active is target_state


@pytest.mark.parametrize("is_active", [True, False])
def test_cannot_toggle_superadmin_activation(is_active: bool) -> None:
    # Arrange
    user = create_user(role=UserRole.SUPERADMIN, is_active=not is_active)
    sut = AccessService()

    # Act & Assert
    with pytest.raises(AccessChangeNotPermittedError):
        sut.toggle_user_activation(user, is_active=is_active)

    assert user.is_active is not is_active


def test_user_can_always_manage_itself() -> None:
    # Arrange
    user = create_user(role=UserRole.USER)
    sut = AccessService()

    # Act & Assert
    assert sut.can_manage_user(user, user) is True


@pytest.mark.parametrize(
    ("subject_role", "target_role", "expected"),
    [
        pytest.param(UserRole.SUPERADMIN, UserRole.ADMIN, True, id="superadmin_manages_admin"),
        pytest.param(UserRole.SUPERADMIN, UserRole.USER, True, id="superadmin_manages_user"),
        pytest.param(UserRole.ADMIN, UserRole.USER, True, id="admin_manages_user"),
        pytest.param(UserRole.ADMIN, UserRole.ADMIN, False, id="admin_cannot_manage_admin"),
        pytest.param(UserRole.ADMIN, UserRole.SUPERADMIN, False, id="admin_cannot_manage_superadmin"),
        pytest.param(UserRole.USER, UserRole.USER, False, id="user_cannot_manage_user"),
    ],
)
def test_can_manage_user_by_role(subject_role: UserRole, target_role: UserRole, expected: bool) -> None:
    # Arrange
    subject = create_user(role=subject_role)
    target = create_user(role=target_role)
    sut = AccessService()

    # Act & Assert
    assert sut.can_manage_user(subject, target) is expected
