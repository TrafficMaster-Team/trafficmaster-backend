import base64
import hashlib
import hmac
from typing import Final, NewType, override

import bcrypt

from trafficmaster.domain.user.ports.password_hasher import PasswordHasher
from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.raw_password import RawPassword

PasswordPepper = NewType("PasswordPepper", str)


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, password_pepper: PasswordPepper) -> None:
        self._password_pepper: Final[PasswordPepper] = password_pepper

    @override
    def hash_password(self, password: RawPassword) -> HashedPassword:

        base64_hmac_password: bytes = self._add_pepper(password, self._password_pepper)
        salt: bytes = bcrypt.gensalt()
        bcrypt_hashed_password: bytes = bcrypt.hashpw(base64_hmac_password, salt)
        return HashedPassword(bcrypt_hashed_password)

    @staticmethod
    def _add_pepper(password: RawPassword, pepper: PasswordPepper) -> bytes:
        hmac_password: bytes = hmac.new(
            key=pepper.encode(),
            msg=password.value.encode(),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(hmac_password)

    @override
    def verify_password(self, *, raw_password: RawPassword, hashed_password: HashedPassword) -> bool:
        base64_hmac_password: bytes = self._add_pepper(raw_password, self._password_pepper)
        return bcrypt.checkpw(base64_hmac_password, hashed_password.password)
