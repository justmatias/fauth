# Testing

FAuth ships a `fauth.testing` module to simplify testing. No complex JWT mocks or real database dependencies needed.

## Dependency Override (recommended for unit tests)

```python
import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from myapp.main import app, auth
from fauth.testing import build_fake_auth_provider

class User(BaseModel):
    id: str
    username: str
    is_active: bool = True
    roles: list[str] = []

@pytest.fixture
def test_client() -> TestClient:
    # 1. Provide a mock test user
    mock_user = User(id="user-123", username="test_user", roles=["admin"])

    # 2. Wire the fake provider with an in-memory user store
    fake = build_fake_auth_provider(users={"user-123": mock_user})

    # 3. Override the dependency functions
    app.dependency_overrides[auth.require_user] = fake.require_user
    app.dependency_overrides[auth.require_active_user] = fake.require_active_user

    yield TestClient(app)

    # Clean up overrides
    app.dependency_overrides.clear()

def test_secure_route(test_client):
    response = test_client.get("/me")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello test_user"}
```

## End-to-end testing with real JWT tokens

If you prefer issuing real tokens in tests, `build_fake_auth_provider` uses safe test defaults (a fixed secret key, short expiry):

```python
@pytest.mark.asyncio
async def test_secure_me_endpoint():
    user = User(id="user-999", username="fake_alice", roles=[])

    # FAuth supplies a pre-made test provider with safe defaults
    test_auth = build_fake_auth_provider(users={"user-999": user})

    # Generate a real JWT token via the test provider
    token_response = await test_auth.login(sub="user-999")

    # Override the dependency so the app uses the test user store
    app.dependency_overrides[auth.require_user] = test_auth.require_user

    # Apply Bearer token
    client = TestClient(app)
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token_response.access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Hello fake_alice"}

    app.dependency_overrides.clear()
```

## Testing utilities reference

| Import                                                | Description                                                           |
| ----------------------------------------------------- | --------------------------------------------------------------------- |
| `build_fake_auth_provider(users?, config_overrides?)` | Creates an `AuthProvider` backed by in-memory fakes                   |
| `fake_auth_config(**overrides)`                       | Returns an `AuthConfig` with safe test defaults                       |
| `FakeUserLoader[T]`                                   | In-memory `UserLoader` — populate with `.add_user(id, user)`          |
| `FakeIdentityLoader[T]`                               | In-memory `IdentityLoader` — populate with `.add_user(id, user)`      |
