from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(plain: str) -> str:
    """Hashes a password using Argon2."""
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifies a plain password against an Argon2 hash."""
    return password_hash.verify(plain, hashed)
