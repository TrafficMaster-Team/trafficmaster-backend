from enum import StrEnum


class UserRole(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"

    @property
    def is_assignable(self) -> bool:
        return self != UserRole.SUPERADMIN

    @property
    def is_changeable(self) -> bool:
        return self != UserRole.SUPERADMIN
