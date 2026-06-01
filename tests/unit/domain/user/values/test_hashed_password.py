import pytest

from trafficmaster.domain.user.errors.password import PasswordCantBeEmptyError
from trafficmaster.domain.user.values.hashed_password import HashedPassword


def test_accepts_non_empty_bytes() -> None:
    sut = HashedPassword(b"some_hash")

    assert sut.password == b"some_hash"


def test_rejects_empty_bytes() -> None:
    with pytest.raises(PasswordCantBeEmptyError):
        HashedPassword(b"")


def test_str_decodes_utf8() -> None:
    sut = HashedPassword(b"hashed_value")

    assert str(sut) == "hashed_value"


def test_equality() -> None:
    assert HashedPassword(b"hash") == HashedPassword(b"hash")
    assert HashedPassword(b"hash") != HashedPassword(b"other")
    assert hash(HashedPassword(b"hash")) == hash(HashedPassword(b"hash"))
