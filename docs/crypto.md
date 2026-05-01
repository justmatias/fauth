# Crypto Utilities

FAuth exposes standalone functions for direct use outside the `AuthProvider`:

## JWT

```python
from fauth import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    create_email_verification_token,
    decode_token,
    AuthConfig
)

config = AuthConfig(secret_key="my-secret")

# Create tokens
access = create_access_token(sub="user-123", auth_config=config)
refresh = create_refresh_token(sub="user-123", auth_config=config)
reset = create_password_reset_token(sub="user-123", auth_config=config)
verify = create_email_verification_token(sub="user-123", auth_config=config)

# With scopes and extra claims
access = create_access_token(
    sub="user-123",
    auth_config=config,
    scopes=["read", "write"],
    extra={"tenant_id": "acme"},
)

# Decode (with optional type validation)
payload = decode_token(access, auth_config=config, expected_type="access")
print(payload.sub)         # "user-123"
print(payload.token_type)  # "access"
print(payload.scopes)      # ["read", "write"]
```

## Password Hashing

Uses Argon2 via [`pwdlib`](https://github.com/frankie567/pwdlib):

```python
from fauth import hash_password, verify_password

hashed = hash_password("my-password")
is_valid = verify_password("my-password", hashed)  # True
```
