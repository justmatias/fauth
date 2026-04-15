# pylint: disable=duplicate-code
import time
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from fauth.core import AuthConfig
from fauth.crypto import create_access_token, hash_password
from fauth.middleware import AuthMiddleware
from fauth.providers import AuthProvider
from fauth.testing import FakeUserLoader


class DummyUser(BaseModel):
    id_: UUID = Field(default_factory=uuid4)
    hashed_password: str = Field(default=hash_password("secret_password"))
    is_active: bool = Field(default=True)


@pytest.fixture
def user() -> DummyUser:
    return DummyUser()


@pytest.fixture
def user_loader() -> FakeUserLoader[DummyUser]:
    return FakeUserLoader()


@pytest.fixture
def provider(
    auth_config: AuthConfig,
    user_loader: FakeUserLoader[DummyUser],
) -> AuthProvider[DummyUser]:
    return AuthProvider(config=auth_config, user_loader=user_loader)


@pytest.fixture
def app(
    auth_config: AuthConfig,
    user_loader: FakeUserLoader[DummyUser],
) -> FastAPI:
    _app = FastAPI()
    _app.add_middleware(
        AuthMiddleware,
        config=auth_config,
        user_loader=user_loader,
    )

    @_app.get("/protected")
    async def protected(request: Request) -> dict[str, Any]:
        return {"id": str(request.state.user.id_)}

    @_app.get("/public")
    async def public() -> dict[str, Any]:
        return {"msg": "ok"}

    return _app


@pytest.fixture
def app_auto_error_off(
    auth_config: AuthConfig,
    user_loader: FakeUserLoader[DummyUser],
) -> FastAPI:
    _app = FastAPI()
    _app.add_middleware(
        AuthMiddleware,
        config=auth_config,
        user_loader=user_loader,
        auto_error=False,
    )

    @_app.get("/maybe-protected")
    async def maybe_protected(request: Request) -> dict[str, Any]:
        user = getattr(request.state, "user", None)
        token = getattr(request.state, "token", None)
        return {"authenticated": user is not None, "has_token": token is not None}

    return _app


@pytest.fixture
def app_with_excludes(
    auth_config: AuthConfig,
    user_loader: FakeUserLoader[DummyUser],
) -> FastAPI:
    _app = FastAPI()
    _app.add_middleware(
        AuthMiddleware,
        config=auth_config,
        user_loader=user_loader,
        exclude_paths=["/health"],
    )

    @_app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok"}

    @_app.get("/protected")
    async def protected(request: Request) -> dict[str, Any]:
        return {"id": str(request.state.user.id_)}

    return _app


@pytest.fixture
def app_with_require_user(
    auth_config: AuthConfig,
    user_loader: FakeUserLoader[DummyUser],
    provider: AuthProvider[DummyUser],
) -> FastAPI:
    _app = FastAPI()
    _app.add_middleware(
        AuthMiddleware,
        config=auth_config,
        user_loader=user_loader,
    )

    @_app.get("/me")
    async def me(
        current_user: DummyUser = Depends(provider.require_user),
    ) -> dict[str, Any]:
        return {"id": str(current_user.id_)}

    return _app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


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
def _populate_user(user_loader: FakeUserLoader[DummyUser], user: DummyUser) -> None:
    user_loader.add_user(str(user.id_), user)
