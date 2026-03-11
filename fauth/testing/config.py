from typing import Any

from fauth.config import AuthConfig


def fake_auth_config(**overrides: Any) -> AuthConfig:
    """Returns an AuthConfig with safe test defaults (fixed secret, short expiry)."""
    defaults = {
        "secret_key": "test-secret-key-do-not-use-in-production",
        "algorithm": "HS256",
        "access_token_expire_minutes": 5,
        "refresh_token_expire_minutes": 10,
        "token_type": "bearer",
    }
    defaults.update(overrides)
    return AuthConfig(**defaults)
