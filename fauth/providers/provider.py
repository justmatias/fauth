from collections.abc import Callable
from typing import Annotated, Any, Generic, TypeVar

from fastapi import Depends, HTTPException, Request, status
from fastapi.security.base import SecurityBase

from fauth.core import (
    AuthConfig,
    InvalidTokenError,
    TokenExpiredError,
    TokenPayload,
    TokenResponse,
)
from fauth.crypto import create_access_token, create_refresh_token, decode_token
from fauth.transports import BearerTransport, Transport

from .protocols import UserLoader

T = TypeVar("T")


class AuthProvider(Generic[T]):
    """
    Main authentication API. Creates tokens, checks user roles,
    and returns dependencies for routes.
    """

    def __init__(
        self,
        config: AuthConfig,
        user_loader: UserLoader[T],
        transport: Transport | None = None,
        token_payload_schema: type[TokenPayload] = TokenPayload,
    ):
        self.config = config
        self.user_loader = user_loader
        self.token_payload_schema = token_payload_schema

        if not transport:
            transport = BearerTransport()
        self.transport = transport

    async def require_user(self, request: Request) -> T:
        """Utility to get the currently authenticated user."""
        token = await self.transport(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        try:
            payload = decode_token(token, self.config, self.token_payload_schema)
        except TokenExpiredError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            ) from e
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e

        user = await self.user_loader(payload)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist",
            )

        return user

    async def require_active_user(self, request: Request) -> T:
        """Utility to get the currently authenticated active user."""
        user = await self.require_user(request)
        if hasattr(user, "is_active") and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        return user

    def require_roles(self, roles: list[str]) -> Callable:
        """Dependency demanding the current user has all specified roles."""

        async def role_checker(
            user: Annotated[T, Depends(self.require_active_user)],
        ) -> T:
            user_roles = getattr(user, "roles", [])
            required_roles = set(roles)
            for role in required_roles:
                if role not in user_roles:
                    raise HTTPException(status_code=403, detail=f"Missing role: {role}")
            return user

        return role_checker

    def require_permissions(self, permissions: list[str]) -> Callable:
        """Dependency demanding the current user has all specified permissions."""

        async def permission_checker(
            user: Annotated[T, Depends(self.require_active_user)],
        ) -> T:
            user_permissions = getattr(user, "permissions", [])
            required_permissions = set(permissions)
            for permission in required_permissions:
                if permission not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: requires {permission} permission",
                    )
            return user

        return permission_checker

    async def login(
        self,
        sub: str,
        scopes: list[str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> TokenResponse:
        """Generates access and refresh tokens, bypassing actual pw check (done elsewhere)."""
        access_token = create_access_token(
            sub=sub,
            config=self.config,
            scopes=scopes,
            extra=extra,
        )
        refresh_token = create_refresh_token(
            sub=sub,
            config=self.config,
            scopes=scopes,
            extra=extra,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=self.config.token_type,
        )

    def get_security_scheme(self) -> SecurityBase:
        """Returns the security scheme for FastAPI OpenAPI documentation."""
        return self.transport.get_security_scheme()
