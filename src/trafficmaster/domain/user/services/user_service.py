from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final

from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.errors.user import RoleAssignmentNotPermittedError
from trafficmaster.domain.user.ports.id_generator import UserIDGenerator
from trafficmaster.domain.user.ports.password_hasher import PasswordHasher
from trafficmaster.domain.user.values.raw_password import RawPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole

if TYPE_CHECKING:
    from trafficmaster.domain.user.values.hashed_password import HashedPassword
    from trafficmaster.domain.user.values.user_id import UserID


class UserService:
    def __init__(self, id_generator: UserIDGenerator, password_hasher: PasswordHasher) -> None:
        self._id_generator: Final[UserIDGenerator] = id_generator
        self._password_hasher: Final[PasswordHasher] = password_hasher

    def create_user(
        self,
        name: Username,
        email: UserEmail,
        raw_password: RawPassword,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Fabric method for creating a new user."""

        if not role.is_assignable:
            msg = "You cannot assign this role to user."
            raise RoleAssignmentNotPermittedError(msg)

        hashed_password: HashedPassword = self._password_hasher.hash_password(password=raw_password)
        user_id: UserID = self._id_generator()
        return User(
            id=user_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )

    def verify_password(self, user: User, raw_password: RawPassword) -> bool:
        """Method for verifying password against user's password."""

        return self._password_hasher.verify_password(raw_password=raw_password, hashed_password=user.hashed_password)

    def change_password(self, user: User, raw_password: RawPassword) -> None:
        """Method for changing user's password."""

        user.hashed_password = self._password_hasher.hash_password(password=raw_password)
        user.updated_at = datetime.now(UTC)

    def change_email(self, user: User, email: UserEmail) -> None:
        """Method for changing user's email."""

        user.email = email
        user.updated_at = datetime.now(UTC)

    def change_name(self, user: User, name: Username) -> None:
        """Method for changing user's name."""

        user.name = name
        user.updated_at = datetime.now(UTC)
