import time

import pytest

from fauth.core import AuthConfig, InvalidTokenError, TokenExpiredError
from fauth.crypto import create_access_token, create_refresh_token, decode_token


def test_create_access_token_returns_valid_jwt(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", config=config)
    payload = decode_token(token, config)

    assert payload.sub == "user-1"
    assert payload.token_type == "access"
    assert isinstance(payload.scopes, list)


def test_create_access_token_includes_scopes(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", config=config, scopes=["read", "write"])
    payload = decode_token(token, config)

    assert payload.scopes == ["read", "write"]


def test_create_access_token_includes_extra_claims(config: AuthConfig) -> None:
    token = create_access_token(
        sub="user-1", config=config, extra={"tenant_id": "acme"}
    )
    payload = decode_token(token, config)

    assert payload.tenant_id == "acme"  # type: ignore[attr-defined]


def test_create_refresh_token_returns_valid_jwt(config: AuthConfig) -> None:
    token = create_refresh_token(sub="user-1", config=config)
    payload = decode_token(token, config)

    assert payload.sub == "user-1"
    assert payload.token_type == "refresh"
    assert isinstance(payload.scopes, list)


def test_create_refresh_token_includes_scopes(config: AuthConfig) -> None:
    token = create_refresh_token(sub="user-1", config=config, scopes=["read", "write"])
    payload = decode_token(token, config)
    assert payload.scopes == ["read", "write"]


def test_create_refresh_token_includes_extra_claims(config: AuthConfig) -> None:
    token = create_refresh_token(
        sub="user-1", config=config, extra={"tenant_id": "acme"}
    )
    payload = decode_token(token, config)
    assert payload.tenant_id == "acme"  # type: ignore[attr-defined]


def test_decode_token_raises_on_expired(expired_config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", config=expired_config)
    time.sleep(1)

    with pytest.raises(TokenExpiredError):
        decode_token(token, expired_config)


def test_decode_token_raises_on_invalid(config: AuthConfig) -> None:
    with pytest.raises(InvalidTokenError):
        decode_token("not.a.valid.jwt", config)


def test_decode_token_raises_on_wrong_secret(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", config=config)

    wrong_config = AuthConfig(secret_key="wrong-secret", algorithm="HS256")

    with pytest.raises(InvalidTokenError):
        decode_token(token, wrong_config)
