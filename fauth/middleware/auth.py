from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from fauth.core import AuthConfig, InvalidTokenError, TokenExpiredError, TokenPayload
from fauth.crypto import decode_token
from fauth.providers.protocols import UserLoader
from fauth.transports import BearerTransport, Transport
from fauth.utils import logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that extracts and validates the Bearer token from the
    Authorization header, then stores the loaded user in ``request.state.user``
    and the decoded payload in ``request.state.token_payload``.

    When ``auto_error=True`` (default), any missing, expired, or invalid token
    produces a 401 JSON response before the route handler is reached.  Set
    ``auto_error=False`` to let unauthenticated requests pass through so that
    route-level dependencies can decide how to handle them.

    Use ``exclude_paths`` to bypass middleware enforcement for specific paths
    such as ``/login`` or ``/health``.
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        app: ASGIApp,
        config: AuthConfig,
        user_loader: UserLoader,
        transport: Transport | None = None,
        token_payload_schema: type[TokenPayload] = TokenPayload,
        auto_error: bool = True,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.config = config
        self.user_loader = user_loader
        self.transport = transport or BearerTransport()
        self.token_payload_schema = token_payload_schema
        self.auto_error = auto_error
        self.exclude_paths = set(exclude_paths or [])

    async def dispatch(  # pylint: disable=too-complex, too-many-return-statements
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        token = await self.transport(request)
        request.state.token = token

        if not token:
            if self.auto_error:
                await logger.error("Authentication failed", reason="Missing token")
                return JSONResponse({"detail": "Not authenticated"}, status_code=401)
            return await call_next(request)

        try:
            payload = decode_token(token, self.config, self.token_payload_schema)
        except TokenExpiredError:
            if self.auto_error:
                await logger.warning("Authentication failed", reason="Token expired")
                return JSONResponse({"detail": "Token expired"}, status_code=401)
            return await call_next(request)  # pragma: no cover
        except InvalidTokenError:
            if self.auto_error:
                await logger.warning("Authentication failed", reason="Invalid token")
                return JSONResponse({"detail": "Invalid token"}, status_code=401)
            return await call_next(request)

        user = await self.user_loader(payload)
        if not user:
            if self.auto_error:
                await logger.warning(
                    "Authentication failed", reason="User not found", sub=payload.sub
                )
                return JSONResponse({"detail": "User does not exist"}, status_code=401)
            return await call_next(request)  # pragma: no cover

        request.state.user = user
        request.state.token_payload = payload
        await logger.debug("User authenticated via middleware", sub=payload.sub)
        return await call_next(request)
