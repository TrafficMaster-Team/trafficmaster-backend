from dataclasses import dataclass, field

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole


@dataclass
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
    role: UserRole = field(default_factory=lambda: UserRole.USER)
    is_active: bool = field(default_factory=lambda: True)
