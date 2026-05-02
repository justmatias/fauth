# API Reference

## `AuthConfig`

Centralized authentication settings, powered by [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). Supports loading values from environment variables out of the box.

| Parameter                                 | Type                | Default           | Description                              |
| ----------------------------------------- | ------------------- | ----------------- | ---------------------------------------- |
| `secret_key`                              | `str`               | _required_        | Secret key used for signing JWTs         |
| `algorithm`                               | `str`               | `"HS256"`         | JWT signing algorithm                    |
| `access_token_expire_minutes`             | `int`               | `15`              | Access token TTL in minutes              |
| `refresh_token_expire_minutes`            | `int`               | `10080` (7 days)  | Refresh token TTL in minutes             |
| `password_reset_token_expire_minutes`     | `int`               | `15`              | Password reset token TTL in minutes      |
| `email_verification_token_expire_minutes` | `int`               | `1440` (1 day)    | Email verification token TTL in minutes  |
| `token_type`                              | `Literal["bearer"]` | `"bearer"`        | Token type for responses                 |

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

## `AuthProvider[T]`

The main orchestrator. Provides FastAPI dependencies for authentication and authorization.

### Constructor

```python
AuthProvider(
    config: AuthConfig,
    user_loader: UserLoader[T],
    identity_loader: IdentityLoader[T] | None = None, # Required for authenticate()
    transport: Transport | None = None,               # Defaults to BearerTransport()
    token_payload_schema: type[TokenPayload] = TokenPayload,
    password_field_name: str = "hashed_password",      # Attribute holding the password hash
    roles_field_name: str = "roles",                   # Attribute holding the user's roles
    permissions_field_name: str = "permissions",       # Attribute holding the user's permissions
    active_status_field_name: str = "is_active",       # Attribute indicating if the user is active
)
```

### Methods

| Method                              | Returns         | Description                                                              |
| ----------------------------------- | --------------- | ------------------------------------------------------------------------ |
| `require_user`                      | `T`             | FastAPI dependency — extracts and validates the token, loads the user    |
| `require_active_user`               | `T`             | Like `require_user`, but also checks `user.is_active`                    |
| `require_roles(roles)`              | `Callable`      | Returns a dependency that demands the user has all specified roles       |
| `require_permissions(perms)`        | `Callable`      | Returns a dependency that demands the user has all specified permissions |
| `authenticate(identifier, password)`| `T`             | Verifies credentials via `IdentityLoader` + password check              |
| `login(sub, scopes?, extra?)`       | `TokenResponse` | Issues access + refresh tokens for a given subject                       |
| `get_security_scheme()`             | `SecurityBase`  | Returns the OpenAPI security scheme for docs                             |

## `UserLoader` Protocol

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

## `IdentityLoader` Protocol

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

## `TokenPayload`

The decoded JWT structure. Accepts extra claims via `model_config = ConfigDict(extra="allow")`.

| Field        | Type                                                                   | Description                              |
| ------------ | ---------------------------------------------------------------------- | ---------------------------------------- |
| `sub`        | `str`                                                                  | Subject (typically user ID)              |
| `exp`        | `int`                                                                  | Expiry timestamp                         |
| `iat`        | `int`                                                                  | Issued-at timestamp                      |
| `jti`        | `str`                                                                  | Unique token ID                          |
| `scopes`     | `list[str]`                                                            | Token scopes (defaults to `[]`)          |
| `token_type` | `Literal["access", "refresh", "password_reset", "email_verification"]` | Distinguishes between token types        |

## `TokenResponse`

Returned by `auth.login()`:

```python
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```
