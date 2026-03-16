import time
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from fauth.core import AuthConfig
from fauth.crypto import create_access_token
from fauth.providers import AuthProvider
from fauth.testing import FakeUserLoader


class DummyUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    is_active: bool = Field(default=True)
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


@pytest.fixture
def user() -> DummyUser:
    return DummyUser(roles=["admin"], permissions=["read", "write"])


@pytest.fixture
def inactive_user() -> DummyUser:
    return DummyUser(is_active=False)


@pytest.fixture
def user_loader() -> FakeUserLoader[DummyUser]:
    return FakeUserLoader()


@pytest.fixture
def provider(
    auth_config: AuthConfig, user_loader: FakeUserLoader[DummyUser]
) -> AuthProvider[DummyUser]:
    return AuthProvider(config=auth_config, user_loader=user_loader)


@pytest.fixture
def fastapi_app(provider: AuthProvider[DummyUser]) -> FastAPI:
    app = FastAPI()

    @app.get("/user")
    def get_user(
        user: DummyUser = provider.require_user(),  # type: ignore[assignment]
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    @app.get("/active-user")
    def get_active_user(
        user: DummyUser = provider.require_active_user(),  # type: ignore[assignment]
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    @app.get("/admin")
    def get_admin(
        user: DummyUser = provider.require_roles("admin"),  # type: ignore[assignment]
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    @app.get("/writer")
    def get_writer(
        user: DummyUser = provider.require_permissions("write"),  # type: ignore[assignment]
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    return app


@pytest.fixture
def client(fastapi_app: FastAPI) -> TestClient:
    return TestClient(fastapi_app)


@pytest.fixture
def user_token(auth_config: AuthConfig, user: DummyUser) -> str:
    return create_access_token(sub=str(user.id_), config=auth_config)


@pytest.fixture
def expired_token(auth_config: AuthConfig) -> str:
    expired_config = AuthConfig(
        secret_key=auth_config.secret_key,
        algorithm=auth_config.algorithm,
        access_token_expire_minutes=0,
    )
    token = create_access_token(sub="any-user", config=expired_config)

    time.sleep(1)
    return token


@pytest.fixture
def inactive_user_token(auth_config: AuthConfig, inactive_user: DummyUser) -> str:
    return create_access_token(sub=str(inactive_user.id_), config=auth_config)


@pytest.fixture
def _populate_user(user_loader: FakeUserLoader[DummyUser], user: DummyUser) -> None:
    user_loader.add_user(str(user.id_), user)


@pytest.fixture
def _populate_inactive_user(
    user_loader: FakeUserLoader[DummyUser], inactive_user: DummyUser
) -> None:
    user_loader.add_user(str(inactive_user.id_), inactive_user)


@pytest.fixture
def no_roles_user() -> DummyUser:
    return DummyUser(roles=[])


@pytest.fixture
def no_perms_user() -> DummyUser:
    return DummyUser(permissions=[])


@pytest.fixture
def _populate_no_roles_user(
    user_loader: FakeUserLoader[DummyUser], no_roles_user: DummyUser
) -> None:
    user_loader.add_user(str(no_roles_user.id_), no_roles_user)


@pytest.fixture
def no_roles_user_token(auth_config: AuthConfig, no_roles_user: DummyUser) -> str:
    return create_access_token(sub=str(no_roles_user.id_), config=auth_config)


@pytest.fixture
def _populate_no_perms_user(
    user_loader: FakeUserLoader[DummyUser], no_perms_user: DummyUser
) -> None:
    user_loader.add_user(str(no_perms_user.id_), no_perms_user)


@pytest.fixture
def no_perms_user_token(auth_config: AuthConfig, no_perms_user: DummyUser) -> str:
    return create_access_token(sub=str(no_perms_user.id_), config=auth_config)
