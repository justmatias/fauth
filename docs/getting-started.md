# Getting Started

FAuth is an ergonomic, plug-and-play authentication library for FastAPI. It eliminates boilerplate around JWT, password hashing, user fetching, and Role-Based Access Control (RBAC) by leveraging FastAPI's Dependency Injection, Pydantic models, and Python Protocols.

## Installation

```bash
pip install fauth
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add fauth
```

---

## Quick Setup

The following example uses **SQLAlchemy async** — a common pattern in production FastAPI applications. The core concepts (user model, loaders, `AuthProvider`) apply to any database layer.

### 1. Define your user model

```python
# models.py
from sqlalchemy import Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    roles: Mapped[str] = mapped_column(String, default="")
    permissions: Mapped[str] = mapped_column(String, default="")
```

> FAuth works with any user object — SQLAlchemy, SQLModel, Tortoise ORM, a plain Pydantic model, or a dataclass. The only requirement is that the object exposes the fields referenced by `FieldNames` (defaults: `hashed_password`, `is_active`, `roles`, `permissions`).

### 2. Implement the `UserLoader` and `IdentityLoader` protocols

FAuth calls these two async callbacks to retrieve users from your data source:

```python
# auth.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fauth import TokenPayload
from .models import User


async def load_user(payload: TokenPayload, session: AsyncSession) -> User | None:
    """Resolve a user from a decoded JWT (used by require_user / require_roles)."""
    result = await session.execute(select(User).where(User.id == payload.sub))
    return result.scalar_one_or_none()


async def load_identity(identifier: str, session: AsyncSession) -> User | None:
    """Resolve a user by username/email (used by authenticate() on login)."""
    result = await session.execute(select(User).where(User.username == identifier))
    return result.scalar_one_or_none()
```

### 3. Create the `AuthProvider`

```python
# auth.py (continued)
from fauth import AuthConfig, AuthProvider

config = AuthConfig(secret_key="change-me-in-production")

auth: AuthProvider[User] = AuthProvider(
    config=config,
    user_loader=load_user,
    identity_loader=load_identity,
)
```

`AuthConfig` reads values from environment variables out of the box (via `pydantic-settings`):

```bash
export SECRET_KEY="my-production-secret"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```python
config = AuthConfig()  # reads SECRET_KEY from environment
```

### 4. Wire it into FastAPI

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

from .auth import auth
from .models import User

app = FastAPI()


@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await auth.authenticate(form.username, form.password)
    return await auth.login(sub=user.id)


@app.get("/me")
async def get_me(user: User = Depends(auth.require_user)):
    return {"id": user.id, "username": user.username}


@app.get("/admin")
async def admin_panel(user: User = Depends(auth.require_roles(["admin"]))):
    return {"message": f"Welcome, {user.username}"}
```

- `/login` — verifies credentials via `authenticate()`, then issues access + refresh tokens via `login()`.
- `/me` — protected: requests without a valid `Bearer` token receive `401 Unauthorized`.
- `/admin` — protected and role-gated: users without the `admin` role receive `403 Forbidden`.

---

## Securing Multiple Routes at Once

Use `SecureAPIRouter` to protect an entire group of routes without adding `Depends` to every function. It also registers the security scheme in OpenAPI, so the **Authorize** button appears in Swagger UI automatically.

```python
from fauth import SecureAPIRouter

secure_router = SecureAPIRouter(auth_provider=auth, prefix="/api/v1", tags=["Protected"])


@secure_router.get("/dashboard")
async def dashboard():
    return {"data": "protected content"}


@secure_router.get("/settings")
async def settings():
    return {"theme": "dark"}


app.include_router(secure_router)
```

---

## Next Steps

| Topic | Page |
| --- | --- |
| Full `AuthConfig` options and environment variables | [API Reference](api-reference.md) |
| Custom field names, token payload, and refresh flow | [Authentication](authentication.md) |
| Role and permission enforcement | [Authorization](authorization.md) |
| Cookie-based or custom token transports | [Transports](transports.md) |
| JWT and password hashing utilities | [Crypto Utilities](crypto.md) |
| Structured logging with structlog | [Logging](logging.md) |
| Error codes and exception types | [Error Handling](error-handling.md) |
