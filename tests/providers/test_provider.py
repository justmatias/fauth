import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fauth.core import AuthConfig
from fauth.crypto import hash_password
from fauth.providers import AuthProvider

from .conftest import DummyUser, FakeUserLoader


def test_require_user_expired_token(client: TestClient, expired_token: str) -> None:
    response = client.get("/user", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


def test_require_user_invalid_token(client: TestClient) -> None:
    response = client.get("/user", headers={"Authorization": "Bearer not.a.real.jwt"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.usefixtures("_populate_user")
def test_require_user_valid(client: TestClient, user_token: str) -> None:
    response = client.get("/user", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200


def test_require_user_unknown_user(client: TestClient, user_token: str) -> None:
    response = client.get("/user", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "User does not exist"


def test_require_user_no_token(client: TestClient) -> None:
    response = client.get("/user")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.usefixtures("_populate_inactive_user")
def test_require_active_user_denied(
    client: TestClient, inactive_user_token: str
) -> None:
    response = client.get(
        "/active-user",
        headers={"Authorization": f"Bearer {inactive_user_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"


@pytest.mark.usefixtures("_populate_user")
def test_require_roles_granted(client: TestClient, user_token: str) -> None:
    response = client.get("/admin", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200


@pytest.mark.usefixtures("_populate_no_roles_user")
def test_require_roles_denied(client: TestClient, no_roles_user_token: str) -> None:
    response = client.get(
        "/admin", headers={"Authorization": f"Bearer {no_roles_user_token}"}
    )
    assert response.status_code == 403
    assert "Missing role: admin" in response.json()["detail"]


@pytest.mark.usefixtures("_populate_user")
def test_require_permissions_granted(client: TestClient, user_token: str) -> None:
    response = client.get("/writer", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200


@pytest.mark.usefixtures("_populate_no_perms_user")
def test_require_permissions_denied(
    client: TestClient, no_perms_user_token: str
) -> None:
    response = client.get(
        "/writer", headers={"Authorization": f"Bearer {no_perms_user_token}"}
    )
    assert response.status_code == 403
    assert "requires write permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_returns_token_response(provider: AuthProvider) -> None:
    result = await provider.login(sub="user-1")

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_authenticate_success(
    provider: AuthProvider[DummyUser],
    identity_loader: FakeUserLoader[DummyUser],
    user: DummyUser,
) -> None:
    password = "secret_password"
    user.hashed_password = hash_password(password)
    identity_loader.add_user("alice", user)

    authenticated_user = await provider.authenticate("alice", password)

    assert authenticated_user.id_ == user.id_
    assert authenticated_user.hashed_password == user.hashed_password


@pytest.mark.asyncio
async def test_authenticate_invalid_password(
    provider: AuthProvider[DummyUser],
    identity_loader: FakeUserLoader[DummyUser],
    user: DummyUser,
) -> None:
    password = "secret_password"
    user.hashed_password = hash_password(password)
    identity_loader.add_user("alice", user)

    with pytest.raises(HTTPException) as excinfo:
        await provider.authenticate("alice", "wrong_password")

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_authenticate_unknown_user(provider: AuthProvider[DummyUser]) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await provider.authenticate("unknown", "password")

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_authenticate_inactive_user(
    provider: AuthProvider[DummyUser],
    identity_loader: FakeUserLoader[DummyUser],
    inactive_user: DummyUser,
) -> None:
    password = "secret_password"
    inactive_user.hashed_password = hash_password(password)
    identity_loader.add_user("alice", inactive_user)

    with pytest.raises(HTTPException) as excinfo:
        await provider.authenticate("alice", password)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_authenticate_custom_password_field(
    auth_config: AuthConfig, user_loader: FakeUserLoader[DummyUser]
) -> None:
    class CustomUser(BaseModel):
        id: str
        pw: str

    ident_loader = FakeUserLoader[CustomUser]()
    provider = AuthProvider(
        config=auth_config,
        user_loader=user_loader,
        identity_loader=ident_loader,
        password_field_name="pw",
    )

    password = "secret_password"
    hashed = hash_password(password)
    user = CustomUser(id="user-1", pw=hashed)
    ident_loader.add_user("alice", user)

    authenticated_user = await provider.authenticate("alice", password)
    assert authenticated_user.id == "user-1"


@pytest.mark.asyncio
async def test_authenticate_no_loader_raises_error(
    auth_config: AuthConfig, user_loader: FakeUserLoader[DummyUser]
) -> None:
    provider = AuthProvider(config=auth_config, user_loader=user_loader)
    with pytest.raises(RuntimeError, match="IdentityLoader must be provided"):
        await provider.authenticate("alice", "password")
