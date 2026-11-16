from trafficmaster.domain.user.values.raw_password import RawPassword
from trafficmaster.infrastructure.adapters.common.password_hasher_bcrypt import BcryptPasswordHasher, PasswordPepper


def test_password_hash_is_salted_and_verification_depends_on_password_and_pepper() -> None:
    hasher = BcryptPasswordHasher(PasswordPepper("test-pepper"))
    raw = RawPassword("SecurePassword123")
    first = hasher.hash_password(raw)
    second = hasher.hash_password(raw)

    assert first.password.startswith(b"$2b$")
    assert first.password != raw.value.encode()
    assert first.password != second.password
    assert hasher.verify_password(raw_password=raw, hashed_password=first)
    assert not hasher.verify_password(raw_password=RawPassword("WrongPassword123"), hashed_password=first)
    other_hasher = BcryptPasswordHasher(PasswordPepper("other-pepper"))
    assert not other_hasher.verify_password(raw_password=raw, hashed_password=first)
