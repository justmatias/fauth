from typing import Protocol

from fastapi import Request, Response


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
