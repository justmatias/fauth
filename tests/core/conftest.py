import pytest

from fauth.core import AuthConfig


@pytest.fixture
def default_config() -> AuthConfig:
    return AuthConfig(secret_key="mysecret")


@pytest.fixture
def custom_config() -> AuthConfig:
    return AuthConfig(
        secret_key="newsecret",
        algorithm="RS256",
        access_token_expire_minutes=5,
        refresh_token_expire_minutes=1440,
    )
