from collections.abc import Mapping
from typing import Final

from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.errors.user import (
    AccessChangeNotPermittedError,
    RoleChangeNotPermittedError,
)
from trafficmaster.domain.user.values.user_role import UserRole

SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPERADMIN: {UserRole.ADMIN, UserRole.USER},
    UserRole.ADMIN: {UserRole.USER},
    UserRole.USER: set(),
}


class AccessService:
    def toggle_admin_role(self, user: User, is_admin: bool) -> None:

        if not user.role.is_changeable:
            msg = f"You are not allowed to change {user.role} role"
            raise RoleChangeNotPermittedError(msg)

        user.role = UserRole.ADMIN if is_admin else UserRole.USER

    def toggle_user_activation(self, user: User, is_active: bool) -> None:

        if not user.role.is_changeable:
            msg = f"You are not allowed to change {user.role} activation"
            raise AccessChangeNotPermittedError(msg)

        user.is_active = is_active

    def can_manage_user(self, subject: User, target: User) -> bool:
        if subject == target:
            return True
        return target in SUBORDINATE_ROLES.get(subject.role, set())
