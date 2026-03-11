import datetime
import uuid
from typing import Any

import jwt

from fauth.config import AuthConfig
from fauth.exceptions import InvalidTokenError, TokenExpiredError
from fauth.schemas import TokenPayload


def create_token(
    sub: str,
    token_type: str,
    expire_minutes: int,
    config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
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

    return jwt.encode(payload, config.secret_key, algorithm=config.algorithm)


def create_access_token(
    sub: str,
    config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    return create_token(
        sub=sub,
        token_type="access",
        expire_minutes=config.access_token_expire_minutes,
        config=config,
        scopes=scopes,
        extra=extra,
    )


def create_refresh_token(
    sub: str,
    config: AuthConfig,
    scopes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    return create_token(
        sub=sub,
        token_type="refresh",
        expire_minutes=config.refresh_token_expire_minutes,
        config=config,
        scopes=scopes,
        extra=extra,
    )


def decode_token(
    token: str,
    config: AuthConfig,
    token_payload_schema: type[TokenPayload] = TokenPayload,
) -> TokenPayload:
    try:
        decoded = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm],
        )
        return token_payload_schema(**decoded)
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError("Invalid token") from e
