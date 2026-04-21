from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from fauth.api import SecureAPIRouter
from fauth.core import AuthConfig
from fauth.crypto import create_access_token
from fauth.providers import AuthProvider
from fauth.testing import FakeUserLoader


class DummyUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    is_active: bool = Field(default=True)


@pytest.fixture
def user() -> DummyUser:
    return DummyUser()


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
def app(provider: AuthProvider[DummyUser]) -> FastAPI:
    _app = FastAPI()

    secured = SecureAPIRouter(auth_provider=provider)

    @secured.get("/secure")
    def secure_route() -> dict[str, Any]:
        return {"msg": "secret"}

    _app.include_router(secured)
    return _app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def user_access_token(auth_config: AuthConfig, user: DummyUser) -> str:
    return create_access_token(sub=str(user.id_), auth_config=auth_config)


@pytest.fixture
def _populate_dummy_user(
    user_loader: FakeUserLoader[DummyUser], user: DummyUser
) -> None:
    user_loader.add_user(str(user.id_), user)


@pytest.fixture
def _populate_inactive_dummy_user(
    user_loader: FakeUserLoader[DummyUser], inactive_user: DummyUser
) -> None:
    user_loader.add_user(str(inactive_user.id_), inactive_user)


@pytest.fixture
def inactive_user_access_token(
    auth_config: AuthConfig, inactive_user: DummyUser
) -> str:
    return create_access_token(sub=str(inactive_user.id_), auth_config=auth_config)
