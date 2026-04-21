import time

import pytest

from fauth.core import AuthConfig, InvalidTokenError, TokenExpiredError
from fauth.crypto import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
)


def test_create_access_token_returns_valid_jwt(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", auth_config=config)
    payload = decode_token(token, auth_config=config)

    assert payload.sub == "user-1"
    assert payload.token_type == "access"
    assert isinstance(payload.scopes, list)


def test_create_access_token_includes_scopes(config: AuthConfig) -> None:
    token = create_access_token(
        sub="user-1", auth_config=config, scopes=["read", "write"]
    )
    payload = decode_token(token, auth_config=config)

    assert payload.scopes == ["read", "write"]


def test_create_access_token_includes_extra_claims(config: AuthConfig) -> None:
    token = create_access_token(
        sub="user-1", auth_config=config, extra={"tenant_id": "acme"}
    )
    payload = decode_token(token, auth_config=config)

    assert payload.tenant_id == "acme"  # type: ignore[attr-defined]


def test_create_refresh_token_returns_valid_jwt(config: AuthConfig) -> None:
    token = create_refresh_token(sub="user-1", auth_config=config)
    payload = decode_token(token, auth_config=config)

    assert payload.sub == "user-1"
    assert payload.token_type == "refresh"
    assert isinstance(payload.scopes, list)


def test_create_refresh_token_includes_scopes(config: AuthConfig) -> None:
    token = create_refresh_token(
        sub="user-1", auth_config=config, scopes=["read", "write"]
    )
    payload = decode_token(token, auth_config=config)
    assert payload.scopes == ["read", "write"]


def test_create_refresh_token_includes_extra_claims(config: AuthConfig) -> None:
    token = create_refresh_token(
        sub="user-1", auth_config=config, extra={"tenant_id": "acme"}
    )
    payload = decode_token(token, auth_config=config)
    assert payload.tenant_id == "acme"  # type: ignore[attr-defined]


def test_decode_token_raises_on_expired(expired_config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", auth_config=expired_config)
    time.sleep(1)

    with pytest.raises(TokenExpiredError):
        decode_token(token, auth_config=expired_config)


def test_decode_token_raises_on_invalid(config: AuthConfig) -> None:
    with pytest.raises(InvalidTokenError):
        decode_token("not.a.valid.jwt", auth_config=config)


def test_decode_token_raises_on_wrong_secret(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", auth_config=config)

    wrong_config = AuthConfig(secret_key="wrong-secret", algorithm="HS256")

    with pytest.raises(InvalidTokenError):
        decode_token(token, auth_config=wrong_config)


def test_decode_token_with_valid_expected_type(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", auth_config=config)

    payload = decode_token(token, auth_config=config, expected_type="access")
    assert payload.token_type == "access"


def test_decode_token_with_invalid_expected_type_raises(config: AuthConfig) -> None:
    token = create_access_token(sub="user-1", auth_config=config)

    with pytest.raises(InvalidTokenError, match="Expected refresh got access"):
        decode_token(token, auth_config=config, expected_type="refresh")


def test_create_password_reset_token_returns_valid_jwt(config: AuthConfig) -> None:
    token = create_password_reset_token(sub="user-1", auth_config=config)
    payload = decode_token(token, auth_config=config)

    assert payload.sub == "user-1"
    assert payload.token_type == "password_reset"
    assert isinstance(payload.scopes, list)


def test_create_password_reset_token_includes_scopes(config: AuthConfig) -> None:
    token = create_password_reset_token(
        sub="user-1", auth_config=config, scopes=["read", "write"]
    )
    payload = decode_token(token, auth_config=config)

    assert payload.scopes == ["read", "write"]


def test_create_password_reset_token_includes_extra_claims(config: AuthConfig) -> None:
    token = create_password_reset_token(
        sub="user-1", auth_config=config, extra={"tenant_id": "acme"}
    )
    payload = decode_token(token, auth_config=config)

    assert payload.tenant_id == "acme"  # type: ignore[attr-defined]
