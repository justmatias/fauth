from typing import Generic, TypeVar

import pytest

from fauth.core import AuthConfig, TokenPayload

T = TypeVar("T")


class FakeUserLoader(Generic[T]):
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


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=5,
        refresh_token_expire_minutes=10,
    )
