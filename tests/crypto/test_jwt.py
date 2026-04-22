import time
from collections.abc import Callable

import pytest

from fauth.core import AuthConfig, InvalidTokenError, TokenExpiredError
from fauth.crypto import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
)


@pytest.mark.parametrize(
    "create_token_function, expected_type",
    [
        (create_access_token, "access"),
        (create_refresh_token, "refresh"),
        (create_password_reset_token, "password_reset"),
        (create_email_verification_token, "email_verification"),
    ],
)
def test_create_token_returns_valid_jwt(
    create_token_function: Callable[..., str], expected_type: str, config: AuthConfig
) -> None:
    token = create_token_function(sub="user-1", auth_config=config)
    payload = decode_token(token, auth_config=config)

    assert payload.sub == "user-1"
    assert payload.token_type == expected_type
    assert isinstance(payload.scopes, list)


@pytest.mark.parametrize(
    "create_token_function",
    [
        create_access_token,
        create_refresh_token,
        create_password_reset_token,
        create_email_verification_token,
    ],
)
def test_create_token_includes_scopes(
    create_token_function: Callable[..., str], config: AuthConfig
) -> None:
    token = create_token_function(
        sub="user-1", auth_config=config, scopes=["read", "write"]
    )
    payload = decode_token(token, auth_config=config)

    assert payload.scopes == ["read", "write"]


@pytest.mark.parametrize(
    "create_token_function",
    [
        create_access_token,
        create_refresh_token,
        create_password_reset_token,
        create_email_verification_token,
    ],
)
def test_create_token_includes_extra_claims(
    create_token_function: Callable[..., str], config: AuthConfig
) -> None:
    token = create_token_function(
        sub="user-1", auth_config=config, extra={"tenant_id": "acme"}
    )
    payload = decode_token(token, auth_config=config)

    assert payload.tenant_id == "acme"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "create_token_function",
    [
        create_access_token,
        create_refresh_token,
        create_password_reset_token,
        create_email_verification_token,
    ],
)
def test_decode_token_raises_on_expired(
    create_token_function: Callable[..., str], expired_config: AuthConfig
) -> None:
    token = create_token_function(sub="user-1", auth_config=expired_config)
    time.sleep(1)

    with pytest.raises(TokenExpiredError):
        decode_token(token, auth_config=expired_config)


def test_decode_token_raises_on_invalid(config: AuthConfig) -> None:
    with pytest.raises(InvalidTokenError):
        decode_token("not.a.valid.jwt", auth_config=config)


@pytest.mark.parametrize(
    "create_token_function",
    [
        create_access_token,
        create_refresh_token,
        create_password_reset_token,
        create_email_verification_token,
    ],
)
def test_decode_token_raises_on_wrong_secret(
    create_token_function: Callable[..., str], config: AuthConfig
) -> None:
    token = create_token_function(sub="user-1", auth_config=config)

    wrong_config = AuthConfig(secret_key="wrong-secret", algorithm="HS256")

    with pytest.raises(InvalidTokenError):
        decode_token(token, auth_config=wrong_config)


@pytest.mark.parametrize(
    "create_token_function, expected_type",
    [
        (create_access_token, "access"),
        (create_refresh_token, "refresh"),
        (create_password_reset_token, "password_reset"),
        (create_email_verification_token, "email_verification"),
    ],
)
def test_decode_token_with_valid_expected_type(
    create_token_function: Callable[..., str], expected_type: str, config: AuthConfig
) -> None:
    token = create_token_function(sub="user-1", auth_config=config)

    payload = decode_token(token, auth_config=config, expected_type=expected_type)
    assert payload.token_type == expected_type


@pytest.mark.parametrize(
    "create_token_function, expected_type, invalid_type",
    [
        (create_access_token, "access", "refresh"),
        (create_refresh_token, "refresh", "access"),
        (create_password_reset_token, "password_reset", "access"),
        (create_email_verification_token, "email_verification", "access"),
    ],
)
def test_decode_token_with_invalid_expected_type_raises(
    create_token_function: Callable[..., str],
    expected_type: str,
    invalid_type: str,
    config: AuthConfig,
) -> None:
    token = create_token_function(sub="user-1", auth_config=config)

    with pytest.raises(
        InvalidTokenError, match=f"Expected {invalid_type} got {expected_type}"
    ):
        decode_token(token, auth_config=config, expected_type=invalid_type)
