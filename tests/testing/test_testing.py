import pytest

from fauth.core import TokenPayload
from fauth.providers import AuthProvider
from fauth.testing import build_fake_auth_provider, fake_auth_config


def test_fake_auth_config_defaults() -> None:
    config = fake_auth_config()

    assert config.secret_key == "test-secret-key-do-not-use-in-production"
    assert config.algorithm == "HS256"
    assert config.access_token_expire_minutes == 5
    assert config.refresh_token_expire_minutes == 10
    assert config.token_type == "bearer"


def test_fake_auth_config_overrides() -> None:
    config = fake_auth_config(
        secret_key="custom-key",
        access_token_expire_minutes=30,
    )

    assert config.secret_key == "custom-key"
    assert config.access_token_expire_minutes == 30


def test_build_fake_auth_provider_no_users() -> None:
    provider = build_fake_auth_provider()

    assert isinstance(provider, AuthProvider)


def test_build_fake_auth_provider_with_users() -> None:
    users = {"user-1": {"name": "Alice"}, "user-2": {"name": "Bob"}}
    provider = build_fake_auth_provider(users=users)

    assert isinstance(provider, AuthProvider)


@pytest.mark.asyncio
async def test_build_fake_auth_provider_users_are_loadable() -> None:
    users = {"user-1": {"name": "Alice"}}
    provider = build_fake_auth_provider(users=users)

    payload = TokenPayload(sub="user-1", exp=0, iat=0, jti="test", token_type="access")
    result = await provider.user_loader(payload)

    assert result == {"name": "Alice"}


@pytest.mark.asyncio
async def test_build_fake_auth_provider_unknown_user_returns_none() -> None:
    provider = build_fake_auth_provider(users={"user-1": {"name": "Alice"}})

    payload = TokenPayload(sub="unknown", exp=0, iat=0, jti="test", token_type="access")
    result = await provider.user_loader(payload)

    assert not result


def test_build_fake_auth_provider_with_config_overrides() -> None:
    provider = build_fake_auth_provider(config_overrides={"secret_key": "my-override"})

    assert provider.config.secret_key == "my-override"
