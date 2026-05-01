# Getting Started

## Define your user model

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

## Implement the `UserLoader` and `IdentityLoader` protocols

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

## Create the AuthProvider

```python
from fauth import AuthConfig, AuthProvider

config = AuthConfig(secret_key="my-super-secret-key")
auth: AuthProvider[User] = AuthProvider(
    config=config,
    user_loader=load_user,
    identity_loader=load_identity,
)
```

## Wire it into FastAPI

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
