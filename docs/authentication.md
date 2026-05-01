# Authentication

FAuth provides a built-in `authenticate()` method on `AuthProvider` that handles credential verification using the `IdentityLoader` protocol and Argon2 password hashing.

## Basic setup

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

## Using `authenticate()` in a login endpoint

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

## Custom password field

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
