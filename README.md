# FAuth

An ergonomic, plug-and-play authentication library for FastAPI.

`fauth` eliminates boilerplate around JWT, password hashing, user fetching, and Role-Based Access Control (RBAC) by leveraging FastAPI's Dependency Injection (`Depends`), Pydantic models, and Python Protocols.

## Features

- **Protocol-Based User Fetching**: Complete inversion of control. You implement a simple `UserLoader` protocol to define how to fetch a user from a token payload.
- **Plug-and-Play Configuration**: Centralized settings via Pydantic (`AuthConfig`). Configure once, inject everywhere.
- **Pluggable Transports**: Extensible `Transport` protocol with a built-in `BearerTransport` for Authorization header tokens.
- **Built-in Password Hashing**: Uses modern Argon2 via `pwdlib`.
- **RBAC**: Flexible `require_roles` and `require_permissions` dependencies for endpoint authorization.
- **Secure Router**: `SecureAPIRouter` applies authentication as a router-level dependency, securing all its routes automatically.
- **Testing Utilities**: Ships fake implementations (`FakeUserLoader`) and a `build_fake_auth_provider()` factory so consumers can write unit tests with zero boilerplate.
- **Type Safety**: Fully annotated for MyPy and IDE integration.

## Quick Start

```bash
pip install fauth
```

```bash
uv add fauth
```

## How to use FAuth

To adopt FAuth, define an async user lookup function (implementing the `UserLoader` protocol), supply an `AuthConfig`, and instantiate the `AuthProvider`. You can then inject the provider directly into FastAPI endpoints.

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fauth import AuthConfig, AuthProvider, TokenPayload, SecureAPIRouter

app = FastAPI()

# 1. Define your internal user model
class User(BaseModel):
    id: str
    username: str
    is_active: bool = True
    roles: list[str] = []

# Mock database
DB: dict[str, User] = {
    "user-123": User(id="user-123", username="alice", roles=["admin"])
}

# 2. Define the callback that retrieves a user from the decoded JWT
async def load_user(payload: TokenPayload) -> User | None:
    return DB.get(payload.sub)

# 3. Instantiate the auth component (ideally wired in DI or at module-level)
config = AuthConfig(secret_key="my-super-secret-key", algorithm="HS256")
auth: AuthProvider[User] = AuthProvider(config=config, user_loader=load_user)

# --- Routes ---

@app.post("/login")
async def login():
    # Example logic: password hashing checks omitted for brevity
    # 4. Use `auth.login` to issue tokens
    return await auth.login(sub="user-123")

@app.get("/me")
async def get_me(user: User = Depends(auth.require_user())):
    # 5. `auth.require_user()` secures the endpoint automatically
    return {"message": f"Hello {user.username}"}

@app.get("/admin")
async def get_admin_data(user: User = Depends(auth.require_roles("admin"))):
    # 6. `auth.require_roles()` enforces RBAC implicitly
    return {"secret_data": "Top secret admin info"}

# --- Securing Multiple Routes ---

# 7. Use `SecureAPIRouter` to protect an entire group of routes.
# Any route added to this router will require an active user automatically.
secure_router = SecureAPIRouter(auth_provider=auth, prefix="/internal", tags=["Protected"])

@secure_router.get("/dashboard")
async def get_dashboard():
    # This endpoint is secured by FAuth without needing Depends in the signature!
    return {"data": "Secure dashboard"}

app.include_router(secure_router)
```

## Custom Token Payload

By default, FAuth decodes JWTs into its built-in `TokenPayload` schema. If you need custom claims in your tokens (e.g., `tenant_id`, `organization_id`), subclass `TokenPayload` and pass it to `AuthProvider`:

```python
from fauth import AuthConfig, AuthProvider, TokenPayload

class MyTokenPayload(TokenPayload):
    tenant_id: str
    plan: str = "free"

auth = AuthProvider(
    config=AuthConfig(secret_key="my-secret"),
    user_loader=load_user,
    token_payload_schema=MyTokenPayload,  # JWTs will be decoded into MyTokenPayload
)
```

When issuing tokens, use the `extra` parameter to encode the custom claims into the JWT:

```python
await auth.login(sub="user-123", extra={"tenant_id": "acme", "plan": "pro"})
```

On the decoding side, your `user_loader` will receive a `MyTokenPayload` instance with fully typed access to `payload.tenant_id` and `payload.plan`.

## Testing your endpoints with FAuth Fakes

FAuth ships with a `fauth.testing` module specifically to simplify testing. No complex JWT mocks or real database dependencies needed — just use `build_fake_auth_provider` to wire up an in-memory auth provider.

```python
import asyncio
import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from myapp.main import app, auth  # Import your FastAPI app and FAuth instance
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

    # 3. Override the internal cached dependency functions.
    # These are the actual callables that FastAPI resolves inside Depends().
    app.dependency_overrides[auth._require_user] = fake._require_user
    app.dependency_overrides[auth._require_active_user] = fake._require_active_user

    yield TestClient(app)

    # Clean up overrides
    app.dependency_overrides.clear()

def test_secure_route(test_client):
    response = test_client.get("/me")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello test_user"}
```

### Alternative: End-to-end testing with real JWT tokens

If you prefer issuing real tokens in tests, `build_fake_auth_provider` uses safe test defaults (a fixed secret key, short expiry) so you can generate tokens without any extra setup.

```python
def test_secure_me_endpoint():
    user = User(id="user-999", username="fake_alice", roles=[])

    # FAuth supplies a pre-made test provider with safe defaults
    test_auth = build_fake_auth_provider(users={"user-999": user})

    # Generate a real JWT token via the test provider
    token_response = asyncio.run(test_auth.login(sub="user-999"))

    # Override the dependency so the app uses the test user store
    app.dependency_overrides[auth._require_user] = test_auth._require_user

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
