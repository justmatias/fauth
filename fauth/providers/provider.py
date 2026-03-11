from collections.abc import Callable
from typing import Any, Generic, TypeVar

from fastapi import Depends, HTTPException, Request, status

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

        # Cache the dependency functions to optimize performance per-request.
        # FastAPI's dependency injection system uses function identity to determine
        # if a dependency has already been executed for a given request.
        # By calling the factory methods once and storing the resulting function objects,
        # FastAPI recognizes them as exactly the same dependency whenever `Depends()` is used.
        # This ensures token decoding and database lookups (user_loader) only happen
        # once per request, even if required by multiple routes or sub-dependencies.
        self._require_user = self._build_require_user_dependency()
        self._require_active_user = self._build_require_active_user_dependency()

    def _build_require_user_dependency(self) -> Callable[..., Any]:
        async def dependency(request: Request) -> T:
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

        return dependency

    def require_user(self) -> Callable:
        """Dependency to get the currently authenticated user."""
        return Depends(self._require_user)  # type: ignore[no-any-return]

    def _build_require_active_user_dependency(self) -> Callable:
        async def dependency(user: T = Depends(self._require_user)) -> T:
            if hasattr(user, "is_active") and not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user",
                )
            return user

        return dependency

    def require_active_user(self) -> Callable:
        """Dependency to get the current user, demanding they be active."""
        return Depends(self._require_active_user)  # type: ignore[no-any-return]

    def require_roles(self, *roles: str) -> Callable:
        """Dependency demanding the user has all specified roles."""

        async def dependency(
            user: T = Depends(self._require_active_user),
        ) -> T:
            user_roles = getattr(user, "roles", [])
            for role in roles:
                if role not in user_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: requires {role} role",
                    )
            return user

        return Depends(dependency)  # type: ignore[no-any-return]

    def require_permissions(self, *permissions: str) -> Callable:
        """Dependency demanding the user has all specified permissions."""

        async def dependency(
            user: T = Depends(self._require_active_user),
        ) -> T:
            user_permissions = getattr(user, "permissions", [])
            for perm in permissions:
                if perm not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: requires {perm} permission",
                    )
            return user

        return Depends(dependency)  # type: ignore[no-any-return]

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
