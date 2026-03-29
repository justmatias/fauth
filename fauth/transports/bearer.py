from fastapi import Request, Response
from fastapi.security import OAuth2PasswordBearer

from fauth.transports.base import Transport


class BearerTransport(Transport):
    """Transport that extracts Bearer token from the Authorization header."""

    def __init__(self, tokenUrl: str = "login"):
        self.scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl, auto_error=False)

    async def __call__(self, request: Request) -> str | None:
        return await self.scheme(request)

    def set_token_response(self, response: Response, token: str) -> None:
        """For Bearer token, we don't set it in a header/cookie here."""

    def clear_token_response(self, response: Response) -> None:
        """For Bearer token, client typically handles removal on their end."""
