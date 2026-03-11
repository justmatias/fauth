from typing import Protocol, TypeVar

from fauth.schemas import TokenPayload

T = TypeVar("T", covariant=True)


class UserLoader(Protocol[T]):
    """Consumer implements this to look up a user from JWT payload."""

    async def __call__(self, token_payload: TokenPayload) -> T | None: ...
