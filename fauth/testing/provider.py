from typing import Any, TypeVar

from fauth.provider import AuthProvider
from fauth.testing.config import fake_auth_config
from fauth.testing.fakes import FakeUserLoader

T = TypeVar("T")


def build_fake_auth_provider(  # noqa: UP047
    users: dict[str, T] | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> AuthProvider[T]:
    """Returns a fully-wired AuthProvider backed by in-memory fakes."""
    config = fake_auth_config(**(config_overrides or {}))
    loader: FakeUserLoader[T] = FakeUserLoader()
    if users:
        for uid, user in users.items():
            loader.add_user(uid, user)

    return AuthProvider(config=config, user_loader=loader)
