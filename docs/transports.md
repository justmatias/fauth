# Custom Transports

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
