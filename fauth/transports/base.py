from typing import Protocol

from fastapi import Request, Response
from fastapi.security.base import SecurityBase


class Transport(Protocol):
    """Abstract transport for extracting and setting authentication tokens."""

    async def __call__(self, request: Request) -> str | None:
        """Extracts the token from the request."""
        ...

    def set_token_response(self, response: Response, token: str) -> None:
        """Sets the token in the response."""
        ...

    def clear_token_response(self, response: Response) -> None:
        """Clears the token from the response."""
        ...

    def get_security_scheme(self) -> SecurityBase:
        """Returns the security scheme for FastAPI OpenAPI documentation."""
        ...
