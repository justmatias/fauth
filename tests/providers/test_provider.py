import pytest
from fastapi.testclient import TestClient

from fauth.providers import AuthProvider


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
    assert "requires admin role" in response.json()["detail"]


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
