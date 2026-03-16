import pytest

from fauth.core import AuthConfig


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=5,
        refresh_token_expire_minutes=10,
    )
