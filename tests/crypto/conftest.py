import pytest

from fauth.core import AuthConfig


@pytest.fixture
def config() -> AuthConfig:
    return AuthConfig(
        secret_key="test-jwt-secret",
        algorithm="HS256",
        access_token_expire_minutes=5,
        refresh_token_expire_minutes=10,
    )


@pytest.fixture
def expired_config() -> AuthConfig:
    return AuthConfig(
        secret_key="test-jwt-secret",
        algorithm="HS256",
        access_token_expire_minutes=0,
        refresh_token_expire_minutes=0,
        password_reset_token_expire_minutes=0,
        email_verification_token_expire_minutes=0,
    )
