import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .conftest import DummyUser


def test_missing_token_returns_401(client: TestClient) -> None:
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_malformed_token_returns_401(client: TestClient) -> None:
    response = client.get(
        "/protected", headers={"Authorization": "Bearer not-a-valid-jwt"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_expired_token_returns_401(client: TestClient, expired_token: str) -> None:
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


@pytest.mark.usefixtures("_populate_user")
def test_valid_token_populates_state(
    client: TestClient, user: DummyUser, user_token: str
) -> None:
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id_)


def test_unknown_user_returns_401(client: TestClient, user_token: str) -> None:
    # user_loader is empty — token is valid but user does not exist
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "User does not exist"


def test_auto_error_off_passes_unauthenticated_request(
    app_auto_error_off: FastAPI,
) -> None:
    client = TestClient(app_auto_error_off)
    response = client.get("/maybe-protected")
    assert response.status_code == 200
    assert response.json()["authenticated"] is False
    assert response.json()["has_token"] is False


@pytest.mark.usefixtures("_populate_user")
def test_auto_error_off_populates_state_when_token_valid(
    app_auto_error_off: FastAPI, user_token: str
) -> None:
    client = TestClient(app_auto_error_off)
    response = client.get(
        "/maybe-protected", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert response.json()["has_token"] is True


def test_raw_token_stored_on_state_even_when_decode_fails(
    app_auto_error_off: FastAPI,
) -> None:
    client = TestClient(app_auto_error_off)
    response = client.get(
        "/maybe-protected", headers={"Authorization": "Bearer not-a-valid-jwt"}
    )
    assert response.status_code == 200
    assert response.json()["authenticated"] is False
    assert response.json()["has_token"] is True


def test_excluded_path_bypasses_enforcement(app_with_excludes: FastAPI) -> None:
    client = TestClient(app_with_excludes)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_non_excluded_path_still_enforced(app_with_excludes: FastAPI) -> None:
    client = TestClient(app_with_excludes)
    response = client.get("/protected")
    assert response.status_code == 401


@pytest.mark.usefixtures("_populate_user")
def test_require_user_reads_from_state_when_middleware_set(
    app_with_require_user: FastAPI, user: DummyUser, user_token: str
) -> None:
    client = TestClient(app_with_require_user)
    response = client.get("/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id_)
