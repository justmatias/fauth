# FAuth

An ergonomic, plug-and-play authentication library for FastAPI.

`fauth` eliminates boilerplate around JWT, password hashing, user fetching, and Role-Based Access Control (RBAC) by leveraging FastAPI's Dependency Injection (`Depends`), Pydantic models, and Python Protocols.

## Features

- **Protocol-Based User Fetching**: Complete inversion of control. You implement a simple `UserLoader` protocol to define how to fetch a user from a token payload.
- **Plug-and-Play Configuration**: Centralized settings via Pydantic (`AuthConfig`). Configure once, inject everywhere.
- **Multiple Transports**: Support for Bearer header tokens and HttpOnly Cookie tokens.
- **Built-in Password Hashing**: Uses modern Argon2 via `pwdlib`.
- **RBAC**: Flexible `require_roles` and `require_permissions` dependencies for endpoint authorization.
- **Pre-built Routes**: Optional pre-configured routers for login, refresh, and logout endpoints.
- **Type Safety**: fully annotated for MyPy and IDE integration.
- **Testing Helpers**: Utilities to make it easy for consumers to write unit tests for endpoints protected by `fauth`.