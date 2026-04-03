# FAuth

An ergonomic, plug-and-play authentication library for FastAPI.

`fauth` eliminates boilerplate around JWT, password hashing, user fetching, and Role-Based Access Control (RBAC) by leveraging FastAPI's Dependency Injection (`Depends`), Pydantic models, and Python Protocols.

[![PyPI version](https://img.shields.io/pypi/v/fauth)](https://pypi.org/project/fauth/)
[![Python versions](https://img.shields.io/pypi/pyversions/fauth)](https://pypi.org/project/fauth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Protocol-Based User Fetching** — Complete inversion of control. You implement a simple `UserLoader` protocol to define how to fetch a user from a token payload.
- **Plug-and-Play Configuration** — Centralized settings via Pydantic (`AuthConfig`). Configure once, inject everywhere.
- **Pluggable Transports** — Extensible `Transport` protocol with a built-in `BearerTransport` for Authorization header tokens.
- **Automatic OpenAPI/Swagger UI Support** — Integrated security schemes that automatically show the "Authorize" button and security lock icons in Swagger UI.
- **Built-in Password Hashing & Crypto** — Modern Argon2 via `pwdlib` and utilities for creating/decoding JWT access and refresh tokens.
- **RBAC** — Flexible `require_roles` and `require_permissions` dependencies for endpoint authorization.
- **Secure Router** — `SecureAPIRouter` applies authentication as a router-level dependency, securing all its routes automatically.
- **Structured Logging** — Built-in `structlog`-based logging for authentication events, token operations, and security failures.
- **Testing Utilities** — Ships fake implementations (`FakeUserLoader`) and a `build_fake_auth_provider()` factory so consumers can write unit tests with zero boilerplate.
- **Type Safety** — Fully annotated for MyPy and IDE integration.

## Installation

```bash
pip install fauth
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add fauth
```

---

## Quick Start

### 1. Define your user model

```python
from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    hashed_password: str
    is_active: bool = True
    roles: list[str] = []
    permissions: list[str] = []
```

### 2. Implement the `UserLoader` and `IdentityLoader` protocols

FAuth uses a callback-based approach. You provide functions that retrieve users from your data source:

```python
from fauth import TokenPayload, hash_password

# Your database, ORM, or any data source
DB: dict[str, User] = {
    "user-123": User(
        id="user-123",
        username="alice",
        hashed_password=hash_password("s3cret"),
        roles=["admin"],
        permissions=["read", "write"],
    ),
}

# UserLoader — resolves a user from a decoded JWT
async def load_user(payload: TokenPayload) -> User | None:
    return DB.get(payload.sub)

# IdentityLoader — resolves a user by identifier (for password authentication)
async def load_identity(identifier: str) -> User | None:
    return next((u for u in DB.values() if u.username == identifier), None)
```

### 3. Create the AuthProvider

```python
from fauth import AuthConfig, AuthProvider

config = AuthConfig(secret_key="my-super-secret-key")
auth: AuthProvider[User] = AuthProvider(
    config=config,
    user_loader=load_user,
    identity_loader=load_identity,
)
```

### 4. Wire it into FastAPI

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.post("/login")
async def login(username: str, password: str):
    user = await auth.authenticate(username, password)
    return await auth.login(sub=user.id)

@app.get("/me")
async def get_me(user: User = Depends(auth.require_user)):
    return {"message": f"Hello {user.username}"}
```

That's it. The `/login` endpoint verifies credentials via `authenticate()`, then issues tokens via `login()`. The `/me` endpoint is protected — requests without a valid `Bearer` token will receive a `401 Unauthorized` response.

---

## Full Example

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fauth import AuthConfig, AuthProvider, TokenPayload, SecureAPIRouter, hash_password

app = FastAPI()

# 1. Define your internal user model
class User(BaseModel):
    id: str
    username: str
    hashed_password: str
    is_active: bool = True
    roles: list[str] = []
    permissions: list[str] = []

# Mock databases
DB: dict[str, User] = {
    "user-123": User(
        id="user-123",
        username="alice",
        hashed_password=hash_password("s3cret"),
        roles=["admin"],
        permissions=["read", "write"],
    )
}

# Identity lookup by username (used by authenticate)
IDENTITY_DB: dict[str, User] = {
    "alice": DB["user-123"],
}

# 2. Define the callback that retrieves a user from the decoded JWT
async def load_user(payload: TokenPayload) -> User | None:
    return DB.get(payload.sub)

# 3. Define the callback that retrieves a user by identifier (for password auth)
async def load_identity(identifier: str) -> User | None:
    return IDENTITY_DB.get(identifier)

# 4. Instantiate the auth component
config = AuthConfig(secret_key="my-super-secret-key", algorithm="HS256")
auth: AuthProvider[User] = AuthProvider(
    config=config,
    user_loader=load_user,
    identity_loader=load_identity,
)

# --- Routes ---

@app.post("/login")
async def login(username: str, password: str):
    # 5. Verify credentials, then issue tokens
    user = await auth.authenticate(username, password)
    return await auth.login(sub=user.id)

@app.get("/me")
async def get_me(user: User = Depends(auth.require_user)):
    # 6. `auth.require_user` secures the endpoint automatically
    return {"message": f"Hello {user.username}"}

@app.get("/admin")
async def get_admin_data(user: User = Depends(auth.require_roles(["admin"]))):
    # 7. `auth.require_roles` enforces RBAC with list of roles
    return {"secret_data": "Top secret admin info"}

# --- Securing Multiple Routes ---

# 8. Use `SecureAPIRouter` to protect an entire group of routes.
# Any route added to this router will require an active user automatically.
# This also enables the "Authorize" button in Swagger UI!
secure_router = SecureAPIRouter(auth_provider=auth, prefix="/internal", tags=["Protected"])

@secure_router.get("/dashboard")
async def get_dashboard():
    # This endpoint is secured by FAuth without needing Depends in the signature!
    return {"data": "Secure dashboard"}

app.include_router(secure_router)
```

---

## API Reference

### `AuthConfig`

Centralized authentication settings, powered by [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). Supports loading values from environment variables out of the box.

| Parameter                      | Type                | Default          | Description                      |
| ------------------------------ | ------------------- | ---------------- | -------------------------------- |
| `secret_key`                   | `str`               | _required_       | Secret key used for signing JWTs |
| `algorithm`                    | `str`               | `"HS256"`        | JWT signing algorithm            |
| `access_token_expire_minutes`  | `int`               | `15`             | Access token TTL in minutes      |
| `refresh_token_expire_minutes` | `int`               | `10080` (7 days) | Refresh token TTL in minutes     |
| `token_type`                   | `Literal["bearer"]` | `"bearer"`       | Token type for responses         |

```python
from fauth import AuthConfig

# Minimal — only secret_key is required
config = AuthConfig(secret_key="my-secret-key")

# Full control
config = AuthConfig(
    secret_key="my-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_minutes=60 * 24,  # 1 day
)
```

Since `AuthConfig` extends `BaseSettings`, you can also load from environment variables:

```bash
export SECRET_KEY="my-secret-from-env"
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

```python
config = AuthConfig()  # Reads from environment
```

### `AuthProvider[T]`

The main orchestrator. Provides FastAPI dependencies for authentication and authorization.

#### Constructor

```python
AuthProvider(
    config: AuthConfig,
    user_loader: UserLoader[T],
    identity_loader: IdentityLoader[T] | None = None, # Required for authenticate()
    transport: Transport | None = None,               # Defaults to BearerTransport()
    token_payload_schema: type[TokenPayload] = TokenPayload,
    password_field_name: str = "hashed_password",      # Attribute on user model holding the hash
)
```

#### Methods

| Method                              | Returns         | Description                                                              |
| ----------------------------------- | --------------- | ------------------------------------------------------------------------ |
| `require_user`                      | `T`             | FastAPI dependency — extracts and validates the token, loads the user    |
| `require_active_user`               | `T`             | Like `require_user`, but also checks `user.is_active`                    |
| `require_roles(roles)`              | `Callable`      | Returns a dependency that demands the user has all specified roles       |
| `require_permissions(perms)`        | `Callable`      | Returns a dependency that demands the user has all specified permissions |
| `authenticate(identifier, password)`| `T`             | Verifies credentials via `IdentityLoader` + password check              |
| `login(sub, scopes?, extra?)`       | `TokenResponse` | Issues access + refresh tokens for a given subject                       |
| `get_security_scheme()`             | `SecurityBase`  | Returns the OpenAPI security scheme for docs                             |

### `UserLoader` Protocol

Your application implements this to tell FAuth how to fetch a user from a decoded JWT:

```python
from fauth import TokenPayload

# As a plain function
async def load_user(token_payload: TokenPayload) -> User | None:
    return await db.get_user(token_payload.sub)

# Or as a callable class
class MyUserLoader:
    def __init__(self, db: Database):
        self.db = db

    async def __call__(self, token_payload: TokenPayload) -> User | None:
        return await self.db.get_user(token_payload.sub)
```

### `IdentityLoader` Protocol

Used by `authenticate()` to look up a user by an identifier (username, email, etc.):

```python
# As a plain function
async def load_identity(identifier: str) -> User | None:
    return await db.get_user_by_username(identifier)

# Or as a callable class
class MyIdentityLoader:
    def __init__(self, db: Database):
        self.db = db

    async def __call__(self, identifier: str) -> User | None:
        return await self.db.get_user_by_username(identifier)
```

### `TokenPayload`

The decoded JWT structure. Accepts extra claims via `model_config = ConfigDict(extra="allow")`.

| Field        | Type                           | Description                              |
| ------------ | ------------------------------ | ---------------------------------------- |
| `sub`        | `str`                          | Subject (typically user ID)              |
| `exp`        | `int`                          | Expiry timestamp                         |
| `iat`        | `int`                          | Issued-at timestamp                      |
| `jti`        | `str`                          | Unique token ID                          |
| `scopes`     | `list[str]`                    | Token scopes (defaults to `[]`)          |
| `token_type` | `Literal["access", "refresh"]` | Distinguishes access from refresh tokens |

### `TokenResponse`

Returned by `auth.login()`:

```python
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

---

## Crypto Utilities

FAuth exposes standalone functions for direct use outside the `AuthProvider`:

### JWT

```python
from fauth import create_access_token, create_refresh_token, decode_token, AuthConfig

config = AuthConfig(secret_key="my-secret")

# Create tokens
access = create_access_token(sub="user-123", config=config)
refresh = create_refresh_token(sub="user-123", config=config)

# With scopes and extra claims
access = create_access_token(
    sub="user-123",
    config=config,
    scopes=["read", "write"],
    extra={"tenant_id": "acme"},
)

# Decode
payload = decode_token(access, config)
print(payload.sub)         # "user-123"
print(payload.token_type)  # "access"
print(payload.scopes)      # ["read", "write"]
```

### Password Hashing

Uses Argon2 via [`pwdlib`](https://github.com/frankie567/pwdlib):

```python
from fauth import hash_password, verify_password

hashed = hash_password("my-password")
is_valid = verify_password("my-password", hashed)  # True
```

---

## Authentication with Password Verification

FAuth provides a built-in `authenticate()` method on `AuthProvider` that handles credential verification using the `IdentityLoader` protocol and Argon2 password hashing.

### Basic setup

```python
from pydantic import BaseModel
from fauth import AuthConfig, AuthProvider, hash_password

class User(BaseModel):
    id: str
    username: str
    hashed_password: str
    is_active: bool = True

# Identity loader retrieves user by username/email/etc.
async def load_identity(identifier: str) -> User | None:
    return await db.get_user_by_username(identifier)

# Token-based user loader (used by require_user)
async def load_user(payload) -> User | None:
    return await db.get_user_by_id(payload.sub)

auth = AuthProvider(
    config=AuthConfig(secret_key="my-secret"),
    user_loader=load_user,
    identity_loader=load_identity,
)
```

### Using `authenticate()` in a login endpoint

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/login")
async def login(username: str, password: str):
    # Verifies password and checks is_active
    user = await auth.authenticate(username, password)
    # Issue tokens
    return await auth.login(sub=user.id)
```

`authenticate()` performs three checks in order:
1. **User exists** — looks up the user via `IdentityLoader`. Raises `401` if not found.
2. **Password is valid** — verifies the plain password against the hashed password stored on the user. Raises `401` if invalid.
3. **User is active** — checks `user.is_active` (if the attribute exists). Raises `401` if inactive.

### Custom password field

By default, `authenticate()` reads the hash from `user.hashed_password`. If your model stores it under a different attribute name, pass `password_field_name`:

```python
class User(BaseModel):
    id: str
    pw_hash: str  # non-standard field name

auth = AuthProvider(
    config=config,
    user_loader=load_user,
    identity_loader=load_identity,
    password_field_name="pw_hash",
)
```

> **Note:** If `AuthProvider` is created without an `identity_loader`, calling `authenticate()` will raise a `RuntimeError`.

---

## Custom Token Payload

If you need custom claims in your tokens (e.g., `tenant_id`, `organization_id`), subclass `TokenPayload` and pass it to `AuthProvider`:

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

When issuing tokens, pass custom claims via the `extra` parameter:

```python
await auth.login(sub="user-123", extra={"tenant_id": "acme", "plan": "pro"})
```

Your `user_loader` will then receive a `MyTokenPayload` instance with typed access to `payload.tenant_id` and `payload.plan`.

---

## RBAC (Roles & Permissions)

### Requiring Roles

```python
@app.get("/admin")
async def admin_panel(user: User = Depends(auth.require_roles(["admin"]))):
    return {"message": "Welcome, admin"}
```

Returns `403 Forbidden` with `{"detail": "Missing role: admin"}` if the user lacks the role.

### Requiring Permissions

```python
@app.get("/reports")
async def reports(user: User = Depends(auth.require_permissions(["read", "reports"]))):
    return {"data": "..."}
```

Returns `403 Forbidden` with `{"detail": "Insufficient permissions: requires read permission"}` if the user lacks any of the required permissions.

> **Note:** FAuth reads roles/permissions from `user.roles` and `user.permissions` attributes respectively. Make sure your user model exposes these fields.

---

## Custom Transports

By default, FAuth uses `BearerTransport`, which extracts the token from the `Authorization: Bearer <token>` header. You can implement the `Transport` protocol to support other strategies (e.g., cookies):

```python
from fastapi import Request, Response
from fastapi.security.base import SecurityBase
from fauth import Transport

class CookieTransport:
    async def __call__(self, request: Request) -> str | None:
        return request.cookies.get("auth_token")

    def set_token_response(self, response: Response, token: str) -> None:
        response.set_cookie("auth_token", token, httponly=True, samesite="lax")

    def clear_token_response(self, response: Response) -> None:
        response.delete_cookie("auth_token")

    def get_security_scheme(self) -> SecurityBase:
        # Return your custom OpenAPI scheme
        ...

# Use it
auth = AuthProvider(config=config, user_loader=load_user, transport=CookieTransport())
```

---

## SecureAPIRouter

`SecureAPIRouter` is a drop-in replacement for `APIRouter` that automatically applies authentication to **all** its routes. It also registers the security scheme in OpenAPI so the "Authorize" button appears in Swagger UI.

```python
from fauth import SecureAPIRouter

secure_router = SecureAPIRouter(
    auth_provider=auth,
    prefix="/api/v1",
    tags=["Protected"],
)

@secure_router.get("/dashboard")
async def dashboard():
    # Automatically secured — no Depends needed in the function signature
    return {"data": "protected content"}

@secure_router.get("/settings")
async def settings():
    return {"theme": "dark"}

app.include_router(secure_router)
```

---

## Testing

FAuth ships a `fauth.testing` module to simplify testing. No complex JWT mocks or real database dependencies needed.

### Dependency Override (recommended for unit tests)

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

### End-to-end testing with real JWT tokens

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

### Testing utilities reference

| Import                                                | Description                                                           |
| ----------------------------------------------------- | --------------------------------------------------------------------- |
| `build_fake_auth_provider(users?, config_overrides?)` | Creates an `AuthProvider` backed by in-memory fakes                   |
| `fake_auth_config(**overrides)`                       | Returns an `AuthConfig` with safe test defaults                       |
| `FakeUserLoader[T]`                                   | In-memory `UserLoader` — populate with `.add_user(id, user)`          |
| `FakeIdentityLoader[T]`                               | In-memory `IdentityLoader` — populate with `.add_user(id, user)`      |

---

## Structured Logging

FAuth uses [`structlog`](https://www.structlog.org/) for structured logging across all security-sensitive operations. **FAuth does not call `structlog.configure()`** — your application owns the processor pipeline. If you never configure structlog, the default `dev` renderer is used (coloured, human-readable text).

### Configuring log output

Configure structlog once in your application startup — FAuth (and any other structlog-based library) will follow:

```python
import structlog

# Development — human-readable coloured text
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ],
)

# Production — JSON lines for log aggregators (Datadog, ELK, etc.)
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)
```

### What gets logged

| Event                   | Level     | Context                                                                        |
| ----------------------- | --------- | ------------------------------------------------------------------------------ |
| `login_token_issued`    | `info`    | `sub`                                                                          |
| `token_decoded`         | `debug`   | `sub`, `token_type`                                                            |
| `user_authenticated`    | `debug`   | `sub`                                                                          |
| `authentication_failed` | `warning` | `reason` (`missing_token`, `token_expired`, `invalid_token`, `user_not_found`) |
| `authorization_failed`  | `warning` | `reason` (`inactive_user`, `missing_role`, `missing_permission`)               |

### Example log output

With `ConsoleRenderer()` (default):

```
2026-04-01 10:30:15 [info     ] login_token_issued             sub=user-123
2026-04-01 10:30:16 [debug    ] token_decoded                  sub=user-123 token_type=access
2026-04-01 10:31:00 [warning  ] authentication_failed          reason=token_expired
```

With `JSONRenderer()`:

```json
{"sub": "user-123", "event": "login_token_issued", "level": "info", "timestamp": "2026-04-01T13:30:15Z"}
{"reason": "token_expired", "event": "authentication_failed", "level": "warning", "timestamp": "2026-04-01T13:31:00Z"}
```

---

## Error Handling

FAuth raises `HTTPException` with standard HTTP status codes:

| Scenario                | Status Code | Detail                                                         |
| ----------------------- | ----------- | -------------------------------------------------------------- |
| Missing token           | `401`       | `"Not authenticated"`                                          |
| Expired token           | `401`       | `"Token expired"`                                              |
| Invalid/malformed token | `401`       | `"Invalid token"`                                              |
| User not found          | `401`       | `"User does not exist"`                                        |
| Invalid credentials     | `401`       | `"Invalid credentials"` (from `authenticate()`)               |
| Inactive user (token)   | `400`       | `"Inactive user"` (from `require_active_user`)                |
| Inactive user (login)   | `401`       | `"Inactive user"` (from `authenticate()`)                     |
| Missing role            | `403`       | `"Missing role: {role}"`                                       |
| Missing permission      | `403`       | `"Insufficient permissions: requires {permission} permission"` |

For programmatic exception handling, FAuth also exposes:

```python
from fauth import FAuthError, InvalidTokenError, TokenExpiredError
```

These are raised by the crypto layer (`decode_token`) and can be caught independently of HTTP responses.

---

## License

MIT
