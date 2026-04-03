from typing import Generic, TypeVar

from fauth.core import TokenPayload

T = TypeVar("T")


class FakeUserLoader(Generic[T]):
    """In-memory UserLoader for tests. Pre-populate with add_user()."""

    def __init__(self) -> None:
        self._users: dict[str, T] = {}

    def add_user(self, user_id: str, user: T) -> None:
        self._users[user_id] = user

    async def __call__(self, token_payload: TokenPayload) -> T | None:
        return self._users.get(token_payload.sub)


class FakeIdentityLoader(Generic[T]):
    def __init__(self) -> None:
        self._users: dict[str, T] = {}

    def add_user(self, user_id: str, user: T) -> None:
        self._users[user_id] = user

    async def __call__(self, identifier: str) -> T | None:
        return self._users.get(identifier)
