import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from fauth.core import AuthConfig
from fauth.crypto import hash_password
from fauth.providers import AuthProvider
from fauth.testing import FakeIdentityLoader

from .conftest import (
    CombinedRolesUser,
    DummyUser,
    EnumRoleUser,
    FakeUserLoader,
    Role,
    StringRoleUser,
)


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


@pytest.mark.usefixtures("_populate_user_with_singular_role")
@pytest.mark.regression
def test_require_roles_with_singular_role_fallback(
    client: TestClient, user_with_singular_role_token: str
) -> None:
    response = client.get(
        "/admin", headers={"Authorization": f"Bearer {user_with_singular_role_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.regression
async def test_require_roles_with_string_role_fallback(
    provider: AuthProvider[DummyUser],
    string_role_user: StringRoleUser,
) -> None:
    role_checker = provider.require_roles(["admin"])
    result = await role_checker(string_role_user)
    assert result.id_ == string_role_user.id_


@pytest.mark.asyncio
@pytest.mark.regression
async def test_require_roles_combined_roles_and_role(
    provider: AuthProvider[DummyUser],
    combined_roles_user: CombinedRolesUser,
) -> None:
    role_checker = provider.require_roles(["admin"])
    result = await role_checker(combined_roles_user)
    assert result.id_ == combined_roles_user.id_


@pytest.mark.asyncio
@pytest.mark.regression
async def test_require_roles_with_enum_role_fallback(
    provider: AuthProvider[DummyUser],
    enum_role_user: EnumRoleUser,
) -> None:
    role_checker = provider.require_roles([Role.ADMIN])
    result = await role_checker(enum_role_user)
    assert result.id_ == enum_role_user.id_


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
@pytest.mark.usefixtures("_populate_identity_user")
async def test_authenticate_success(
    provider: AuthProvider[DummyUser],
    user: DummyUser,
    password: str,
) -> None:
    authenticated_user = await provider.authenticate("alice", password)

    assert authenticated_user.id_ == user.id_
    assert authenticated_user.hashed_password == user.hashed_password


@pytest.mark.asyncio
@pytest.mark.usefixtures("_populate_identity_user")
async def test_authenticate_invalid_password(provider: AuthProvider[DummyUser]) -> None:
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
@pytest.mark.usefixtures("_populate_identity_inactive_user")
async def test_authenticate_inactive_user(
    provider: AuthProvider[DummyUser],
    password: str,
) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await provider.authenticate("alice", password)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_authenticate_custom_password_field(auth_config: AuthConfig) -> None:
    class CustomUser(BaseModel):
        id: str
        pw: str = Field(default=hash_password("secret_password"))

    identity_loader = FakeIdentityLoader[CustomUser]()
    user_loader = FakeUserLoader[CustomUser]()

    provider = AuthProvider(
        config=auth_config,
        user_loader=user_loader,
        identity_loader=identity_loader,
        password_field_name="pw",
    )

    identity_loader.add_user("alice", CustomUser(id="user-1"))

    authenticated_user = await provider.authenticate("alice", "secret_password")
    assert authenticated_user.id == "user-1"


@pytest.mark.asyncio
async def test_authenticate_no_loader_raises_error(
    auth_config: AuthConfig, user_loader: FakeUserLoader[DummyUser]
) -> None:
    provider = AuthProvider(config=auth_config, user_loader=user_loader)
    with pytest.raises(RuntimeError, match="IdentityLoader must be provided"):
        await provider.authenticate("alice", "password")


@pytest.mark.asyncio
@pytest.mark.usefixtures("_populate_user")
async def test_refresh_success(
    provider: AuthProvider[DummyUser], refresh_token: str
) -> None:
    result = await provider.refresh(refresh_token)
    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token_type(
    provider: AuthProvider[DummyUser], user_token: str
) -> None:
    # user_token is an access token, not a refresh token
    with pytest.raises(HTTPException) as excinfo:
        await provider.refresh(user_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid token type"


@pytest.mark.asyncio
async def test_refresh_unknown_user(
    provider: AuthProvider[DummyUser], refresh_token: str
) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await provider.refresh(refresh_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "User does not exist"


@pytest.mark.asyncio
@pytest.mark.usefixtures("_populate_inactive_user")
async def test_refresh_inactive_user(
    provider: AuthProvider[DummyUser], inactive_user_refresh_token: str
) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await provider.refresh(inactive_user_refresh_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_refresh_expired_token(
    provider: AuthProvider[DummyUser], expired_refresh_token: str
) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await provider.refresh(expired_refresh_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Token expired"


@pytest.mark.asyncio
async def test_refresh_invalid_token(provider: AuthProvider[DummyUser]) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await provider.refresh("invalid.token.str")
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid token"
