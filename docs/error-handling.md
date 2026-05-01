# Error Handling

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
