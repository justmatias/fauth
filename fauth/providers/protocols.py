from typing import Protocol, TypeVar

from fauth.core import TokenPayload

T = TypeVar("T", covariant=True)


class UserLoader(Protocol[T]):
    """Consumer implements this to look up a user from JWT payload."""

    async def __call__(self, token_payload: TokenPayload) -> T | None: ...


class IdentityLoader(Protocol[T]):
    """Look up a user from an identifier (username, email, etc.)."""

    async def __call__(self, identifier: str) -> T | None: ...
