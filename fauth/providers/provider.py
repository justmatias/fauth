import enum
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
from fauth.crypto import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from fauth.transports import BearerTransport, Transport
from fauth.utils import logger

from .protocols import IdentityLoader, UserLoader

T = TypeVar("T")


class AuthProvider(Generic[T]):
    """
    Main authentication API. Creates tokens, checks user roles,
    and returns dependencies for routes.
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        config: AuthConfig,
        user_loader: UserLoader[T],
        identity_loader: IdentityLoader[T] | None = None,
        transport: Transport | None = None,
        token_payload_schema: type[TokenPayload] = TokenPayload,
        password_field_name: str = "hashed_password",
    ):
        self.config = config
        self.user_loader = user_loader
        self.identity_loader = identity_loader
        self.token_payload_schema = token_payload_schema
        self.password_field_name = password_field_name

        if not transport:
            transport = BearerTransport()
        self.transport = transport

    async def require_user(self, request: Request) -> T:
        """Utility to get the currently authenticated user.

        If AuthMiddleware is registered, reads directly from request.state (fast path).
        Otherwise extracts and validates the Bearer token from the Authorization header.
        """
        user: T | None = getattr(request.state, "user", None)
        if user:
            return user

        token = await self.transport(request)
        if not token:
            await logger.error("Authentication failed", reason="Missing token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        payload = await self.verify_token(token)

        await logger.debug(
            "Token decoded", sub=payload.sub, token_type=payload.token_type
        )

        user = await self.user_loader(payload)
        if not user:
            await logger.warning(
                "Authentication failed", reason="User not found", sub=payload.sub
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist",
            )

        await logger.debug("User authenticated", sub=payload.sub)
        return user

    async def require_active_user(self, request: Request) -> T:
        """Utility to get the currently authenticated active user."""
        user = await self.require_user(request)
        if hasattr(user, "is_active") and not user.is_active:
            await logger.warning("Authorization failed", reason="Inactive user")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        return user

    def require_roles(self, required_roles: list[str | enum.Enum]) -> Callable:
        """Dependency demanding the current user has all specified roles."""

        async def role_checker(
            user: Annotated[T, Depends(self.require_active_user)],
        ) -> T:
            roles = list(getattr(user, "roles", []))
            role = getattr(user, "role", None)

            if role is not None:
                roles.append(role)

            required_roles_set = set(required_roles)
            for role in required_roles_set:
                if role not in roles:
                    await logger.error(
                        "Authorization failed",
                        reason="Missing role",
                        required_role=role,
                    )
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
                    await logger.error(
                        "Authorization failed",
                        reason="Missing permission",
                        required_permission=permission,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: requires {permission} permission",
                    )
            return user

        return permission_checker

    async def authenticate(self, identifier: str, password: str) -> T:
        """
        Authenticates a user by their identifier and password.
        Returns the user if valid and active, otherwise raises HTTPException.
        """
        if not self.identity_loader:
            raise RuntimeError("IdentityLoader must be provided to use authenticate()")

        user = await self.identity_loader(identifier)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        hashed = getattr(user, self.password_field_name, None)
        if not hashed or not verify_password(password, hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Ensure user is active if it has is_active attribute
        if hasattr(user, "is_active") and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        return user

    async def login(
        self,
        sub: str,
        scopes: list[str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> TokenResponse:
        """Generates access and refresh tokens, bypassing actual pw check (done elsewhere)."""
        await logger.info("Login token issued", sub=sub)
        access_token = create_access_token(
            sub=sub,
            auth_config=self.config,
            scopes=scopes,
            extra=extra,
        )
        refresh_token = create_refresh_token(
            sub=sub,
            auth_config=self.config,
            scopes=scopes,
            extra=extra,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=self.config.token_type,
        )

    async def verify_token(
        self, token: str, expected_type: str | None = None
    ) -> TokenPayload:
        """Validates a JWT and handles converting potential exceptions into HTTPExceptions."""
        try:
            return decode_token(
                token,
                auth_config=self.config,
                token_payload_schema=self.token_payload_schema,
                expected_type=expected_type,
            )
        except TokenExpiredError as e:
            await logger.warning("Token validation failed", reason="Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            ) from e
        except InvalidTokenError as e:
            await logger.warning("Token validation failed", reason=e.message)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
            ) from e

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Validates a refresh token and generates new access and refresh tokens."""
        await logger.info("Refreshing user token...")
        payload = await self.verify_token(refresh_token, expected_type="refresh")

        user = await self.user_loader(payload)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist",
            )

        if hasattr(user, "is_active") and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        token_response = await self.login(sub=payload.sub)
        await logger.info("Token refreshed", sub=payload.sub)
        return token_response

    def get_security_scheme(self) -> SecurityBase:
        """Returns the security scheme for FastAPI OpenAPI documentation."""
        return self.transport.get_security_scheme()
