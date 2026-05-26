from dataclasses import dataclass
from datetime import datetime
from typing import Self, TypedDict
from uuid import UUID

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole


class SerializedUser(TypedDict):
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    password: str
    created_at: str
    updated_at: str


@dataclass(eq=False)
class User(BaseEntity[UserID]):
    """
    User entity.
    params:
        name: unique username,
        email: unique email address,
        hashed_password: bcrypt-hashed password,
        role: USER, ADMIN, or SUPERADMIN,
        is_active: whether the account is enabled.
    """

    name: Username
    email: UserEmail
    hashed_password: HashedPassword
    role: UserRole = UserRole.USER
    is_active: bool = True

    def serialize(self) -> SerializedUser:
        return {
            "id": str(self.id),
            "email": str(self.email),
            "name": str(self.name),
            "role": self.role.value,
            "is_active": self.is_active,
            "password": self.hashed_password.password.decode("utf-8"),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: SerializedUser) -> Self:
        return cls(
            id=UserID(UUID(data["id"])),
            name=Username(data["name"]),
            email=UserEmail(data["email"]),
            hashed_password=HashedPassword(data["password"].encode("utf-8")),
            role=UserRole(data["role"]),
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
