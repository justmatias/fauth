# pylint: disable=duplicate-code
from importlib.metadata import version

from .api import SecureAPIRouter
from .core import (
    AuthConfig,
    FAuthError,
    InvalidTokenError,
    TokenExpiredError,
    TokenPayload,
    TokenResponse,
)
from .crypto import (
    create_access_token,
    create_refresh_token,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from .middleware import AuthMiddleware
from .providers import AuthProvider, UserLoader
from .transports import BearerTransport, Transport

__version__ = version("fauth")

__all__ = [
    "AuthConfig",
    "AuthMiddleware",
    "AuthProvider",
    "BearerTransport",
    "FAuthError",
    "InvalidTokenError",
    "SecureAPIRouter",
    "TokenExpiredError",
    "TokenPayload",
    "TokenResponse",
    "Transport",
    "UserLoader",
    "create_access_token",
    "create_refresh_token",
    "create_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
