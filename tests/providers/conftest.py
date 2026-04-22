import datetime
import enum
from typing import Any
from uuid import UUID, uuid4

import pytest
import time_machine
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from fauth.core import AuthConfig
from fauth.crypto import create_access_token, create_refresh_token, hash_password
from fauth.providers import AuthProvider
from fauth.testing import FakeIdentityLoader, FakeUserLoader


class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class DummyUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    hashed_password: str = Field(default=hash_password("secret_password"))
    is_active: bool = Field(default=True)
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class StringRoleUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    is_active: bool = Field(default=True)
    role: str = "admin"


class EnumRoleUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    is_active: bool = Field(default=True)
    role: Role = Role.ADMIN


class CombinedRolesUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    is_active: bool = Field(default=True)
    roles: list[str] = Field(default_factory=lambda: ["user"])
    role: str = "admin"


@pytest.fixture
def user() -> DummyUser:
    return DummyUser(roles=["admin"], permissions=["read", "write"])


@pytest.fixture
def inactive_user() -> DummyUser:
    return DummyUser(is_active=False)


@pytest.fixture
def string_role_user() -> StringRoleUser:
    return StringRoleUser()


@pytest.fixture
def enum_role_user() -> EnumRoleUser:
    return EnumRoleUser()


@pytest.fixture
def combined_roles_user() -> CombinedRolesUser:
    return CombinedRolesUser()


@pytest.fixture
def user_loader() -> FakeUserLoader[DummyUser]:
    return FakeUserLoader()


@pytest.fixture
def identity_loader() -> FakeIdentityLoader[DummyUser]:
    return FakeIdentityLoader()


@pytest.fixture
def provider(
    auth_config: AuthConfig,
    user_loader: FakeUserLoader[DummyUser],
    identity_loader: FakeIdentityLoader[DummyUser],
) -> AuthProvider[DummyUser]:
    return AuthProvider(
        config=auth_config,
        user_loader=user_loader,
        identity_loader=identity_loader,
    )


@pytest.fixture
def fastapi_app(provider: AuthProvider[DummyUser]) -> FastAPI:
    app = FastAPI()

    @app.get("/user")
    def get_user(
        user: DummyUser = Depends(provider.require_user),
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    @app.get("/active-user")
    def get_active_user(
        user: DummyUser = Depends(provider.require_active_user),
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    @app.get("/admin")
    def get_admin(
        user: DummyUser = Depends(provider.require_roles(["admin"])),
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    @app.get("/writer")
    def get_writer(
        user: DummyUser = Depends(provider.require_permissions(["write"])),
    ) -> dict[str, Any]:
        return {"id": str(user.id_)}

    return app


@pytest.fixture
def client(fastapi_app: FastAPI) -> TestClient:
    return TestClient(fastapi_app)


@pytest.fixture
def user_token(auth_config: AuthConfig, user: DummyUser) -> str:
    return create_access_token(sub=str(user.id_), auth_config=auth_config)


@pytest.fixture
def expired_token(auth_config: AuthConfig) -> str:
    with time_machine.travel(
        datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
    ):
        return create_access_token(sub="any-user", auth_config=auth_config)


@pytest.fixture
def inactive_user_token(auth_config: AuthConfig, inactive_user: DummyUser) -> str:
    return create_access_token(sub=str(inactive_user.id_), auth_config=auth_config)


@pytest.fixture
def refresh_token(auth_config: AuthConfig, user: DummyUser) -> str:
    return create_refresh_token(sub=str(user.id_), auth_config=auth_config)


@pytest.fixture
def expired_refresh_token(auth_config: AuthConfig) -> str:
    with time_machine.travel(
        datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
    ):
        return create_refresh_token(sub="any-user", auth_config=auth_config)


@pytest.fixture
def inactive_user_refresh_token(
    auth_config: AuthConfig, inactive_user: DummyUser
) -> str:
    return create_refresh_token(sub=str(inactive_user.id_), auth_config=auth_config)


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
    return create_access_token(sub=str(no_roles_user.id_), auth_config=auth_config)


@pytest.fixture
def _populate_no_perms_user(
    user_loader: FakeUserLoader[DummyUser], no_perms_user: DummyUser
) -> None:
    user_loader.add_user(str(no_perms_user.id_), no_perms_user)


@pytest.fixture
def no_perms_user_token(auth_config: AuthConfig, no_perms_user: DummyUser) -> str:
    return create_access_token(sub=str(no_perms_user.id_), auth_config=auth_config)


@pytest.fixture
def _populate_identity_user(
    identity_loader: FakeIdentityLoader[DummyUser], user: DummyUser
) -> None:
    identity_loader.add_user("alice", user)


@pytest.fixture
def _populate_identity_inactive_user(
    identity_loader: FakeIdentityLoader[DummyUser], inactive_user: DummyUser
) -> None:
    identity_loader.add_user("alice", inactive_user)


@pytest.fixture
def user_with_singular_role() -> DummyUser:
    return DummyUser(roles=["admin"])


@pytest.fixture
def _populate_user_with_singular_role(
    user_loader: FakeUserLoader[DummyUser], user_with_singular_role: DummyUser
) -> None:
    user_loader.add_user(str(user_with_singular_role.id_), user_with_singular_role)


@pytest.fixture
def user_with_singular_role_token(
    auth_config: AuthConfig, user_with_singular_role: DummyUser
) -> str:
    return create_access_token(
        sub=str(user_with_singular_role.id_), auth_config=auth_config
    )


@pytest.fixture
def password() -> str:
    return "secret_password"
