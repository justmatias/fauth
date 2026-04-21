import datetime
import uuid
from typing import Any

import jwt as pyjwt

from fauth.core import AuthConfig, InvalidTokenError, TokenExpiredError, TokenPayload


def create_token(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    sub: str,
    token_type: str,
    expire_minutes: int,
    config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.datetime.now(datetime.UTC)
    exp = now + datetime.timedelta(minutes=expire_minutes)

    payload = {
        "sub": sub,
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "jti": str(uuid.uuid4()),
        "token_type": token_type,
        "scopes": scopes or [],
        **(extra or {}),
    }

    return pyjwt.encode(payload, config.secret_key, algorithm=config.algorithm)


def create_access_token(
    *,
    sub: str,
    auth_config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    return create_token(
        sub=sub,
        token_type="access",
        expire_minutes=auth_config.access_token_expire_minutes,
        config=auth_config,
        scopes=scopes,
        extra=extra,
    )


def create_refresh_token(
    *,
    sub: str,
    auth_config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    return create_token(
        sub=sub,
        token_type="refresh",
        expire_minutes=auth_config.refresh_token_expire_minutes,
        config=auth_config,
        scopes=scopes,
        extra=extra,
    )


def create_password_reset_token(
    *,
    sub: str,
    auth_config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    return create_token(
        sub=sub,
        token_type="password_reset",
        expire_minutes=auth_config.password_reset_token_expire_minutes,
        config=auth_config,
        scopes=scopes,
        extra=extra,
    )


def decode_token(
    token: str,
    *,
    auth_config: AuthConfig,
    token_payload_schema: type[TokenPayload] = TokenPayload,
    expected_type: str | None = None,
) -> TokenPayload:
    try:
        decoded = pyjwt.decode(
            token,
            auth_config.secret_key,
            algorithms=[auth_config.algorithm],
        )
        payload = token_payload_schema(**decoded)
        if expected_type and payload.token_type != expected_type:
            raise InvalidTokenError(
                f"Expected {expected_type} got {payload.token_type}"
            )
        return payload
    except pyjwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired") from e
    except pyjwt.InvalidTokenError as e:
        raise InvalidTokenError("Failure when decoding token") from e
