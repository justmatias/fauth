# FAuth

An ergonomic, plug-and-play authentication library for FastAPI.

`fauth` eliminates boilerplate around JWT, password hashing, user fetching, and Role-Based Access Control (RBAC) by leveraging FastAPI's Dependency Injection (`Depends`), Pydantic models, and Python Protocols.

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
