from fauth.crypto import hash_password, verify_password


def test_hash_password_returns_argon2_hash() -> None:
    hashed = hash_password("my-password")

    assert isinstance(hashed, str)
    assert hashed != "my-password"
    assert "$argon2" in hashed


def test_hash_password_produces_different_hashes_per_call() -> None:
    h1 = hash_password("same-password")
    h2 = hash_password("same-password")
    assert h1 != h2


def test_verify_password_correct() -> None:
    hashed = hash_password("correct-password")
    assert verify_password("correct-password", hashed)


def test_verify_password_incorrect() -> None:
    hashed = hash_password("correct-password")
    assert not verify_password("wrong-password", hashed)
