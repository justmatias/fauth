from importlib.metadata import version

from .config import AuthConfig
from .protocols import UserLoader
from .provider import AuthProvider
from .router import SecureAPIRouter
from .schemas import TokenPayload, TokenResponse

__version__ = version("fauth")

__all__ = [
    "AuthConfig",
    "AuthProvider",
    "SecureAPIRouter",
    "TokenPayload",
    "TokenResponse",
    "UserLoader",
]
