from tests.unit.factories.values import (
    create_password_hash,
    create_user_email,
    create_user_id,
    create_username,
)
from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole


def create_user(
    user_id: UserID | None = None,
    username: Username | None = None,
    password_hash: HashedPassword | None = None,
    role: UserRole = UserRole.USER,
    email: UserEmail | None = None,
    is_active: bool | None = None,
) -> User:
    if is_active is None:
        is_active = True

    return User(
        id=user_id or create_user_id(),
        email=email or create_user_email(),
        name=username or create_username(),
        hashed_password=password_hash or create_password_hash(),
        role=role,
        is_active=is_active,
    )
