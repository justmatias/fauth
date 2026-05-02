# FAuth

An ergonomic, plug-and-play authentication library for FastAPI.

`fauth` eliminates boilerplate around JWT, password hashing, user fetching, and Role-Based Access Control (RBAC) by leveraging FastAPI's Dependency Injection (`Depends`), Pydantic models, and Python Protocols.

[![Dependabot Updates](https://github.com/justmatias/fauth/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/justmatias/fauth/actions/workflows/dependabot/dependabot-updates)
[![PyPI version](https://img.shields.io/pypi/v/fauth)](https://pypi.org/project/fauth/)
[![Python versions](https://img.shields.io/pypi/pyversions/fauth)](https://pypi.org/project/fauth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Protocol-Based User Fetching** — Complete inversion of control via `UserLoader` and `IdentityLoader` protocols.
- **Plug-and-Play Configuration** — Centralized settings via Pydantic (`AuthConfig`). Configure once, inject everywhere.
- **Pluggable Transports** — Extensible `Transport` protocol with a built-in `BearerTransport`.
- **Automatic OpenAPI/Swagger UI Support** — Integrated security schemes with "Authorize" button in Swagger UI.
- **Built-in Password Hashing & JWT Crypto** — Argon2 via `pwdlib` and utilities for creating/decoding access and refresh tokens.
- **RBAC** — `require_roles` and `require_permissions` dependencies with customizable user model field names.
- **Secure Router** — `SecureAPIRouter` secures all its routes automatically.
- **Structured Logging** — Built-in `structlog`-based logging.
- **Type Safe** — Fully annotated for MyPy and IDE integration.

## Installation

```bash
pip install fauth
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add fauth
```

## Quick Start

```python
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fauth import AuthConfig, AuthProvider, TokenPayload, hash_password

class User(BaseModel):
    id: str
    username: str
    hashed_password: str
    is_active: bool = True
    roles: list[str] = []
    permissions: list[str] = []

DB: dict[str, User] = {
    "user-123": User(id="user-123", username="alice", hashed_password=hash_password("s3cret"), roles=["admin"]),
}

async def load_user(payload: TokenPayload) -> User | None:
    return DB.get(payload.sub)

async def load_identity(identifier: str) -> User | None:
    return next((u for u in DB.values() if u.username == identifier), None)

config = AuthConfig(secret_key="my-super-secret-key")
auth: AuthProvider[User] = AuthProvider(config=config, user_loader=load_user, identity_loader=load_identity)

app = FastAPI()

@app.post("/login")
async def login(username: str, password: str):
    user = await auth.authenticate(username, password)
    return await auth.login(sub=user.id)

@app.get("/me")
async def get_me(user: User = Depends(auth.require_user)):
    return {"message": f"Hello {user.username}"}
```

---

:book: **Full documentation** at [fauth.readthedocs.io](https://fauth.readthedocs.io/)

## License

MIT
