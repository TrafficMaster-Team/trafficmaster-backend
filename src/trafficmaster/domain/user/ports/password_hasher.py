from typing import Protocol

from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.raw_password import RawPassword


class PasswordHasher(Protocol):
    def hash_password(self, password: RawPassword) -> HashedPassword: ...

    def verify_password(self, *, raw_password: RawPassword, hashed_password: HashedPassword) -> bool: ...
