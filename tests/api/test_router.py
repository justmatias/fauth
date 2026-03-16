import pytest
from fastapi.testclient import TestClient


def test_secure_router_denies_unauthenticated(client: TestClient) -> None:
    response = client.get("/secure")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.usefixtures("_populate_dummy_user")
def test_secure_router_allows_authenticated(
    client: TestClient,
    user_access_token: str,
) -> None:
    response = client.get(
        "/secure", headers={"Authorization": f"Bearer {user_access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "secret"


@pytest.mark.usefixtures("_populate_inactive_dummy_user")
def test_secure_router_denies_inactive_user(
    client: TestClient,
    inactive_user_access_token: str,
) -> None:
    response = client.get(
        "/secure", headers={"Authorization": f"Bearer {inactive_user_access_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"
