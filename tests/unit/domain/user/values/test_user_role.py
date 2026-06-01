import pytest

from trafficmaster.domain.user.values.user_role import UserRole


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        pytest.param(UserRole.USER, True, id="user"),
        pytest.param(UserRole.ADMIN, True, id="admin"),
        pytest.param(UserRole.SUPERADMIN, False, id="superadmin"),
    ],
)
def test_is_assignable(role: UserRole, expected: bool) -> None:
    assert role.is_assignable is expected


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        pytest.param(UserRole.USER, True, id="user"),
        pytest.param(UserRole.ADMIN, True, id="admin"),
        pytest.param(UserRole.SUPERADMIN, False, id="superadmin"),
    ],
)
def test_is_changeable(role: UserRole, expected: bool) -> None:
    assert role.is_changeable is expected
