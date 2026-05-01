# SecureAPIRouter

`SecureAPIRouter` is a drop-in replacement for `APIRouter` that automatically applies authentication to **all** its routes. It also registers the security scheme in OpenAPI so the "Authorize" button appears in Swagger UI.

```python
from fauth import SecureAPIRouter

secure_router = SecureAPIRouter(
    auth_provider=auth,
    prefix="/api/v1",
    tags=["Protected"],
)

@secure_router.get("/dashboard")
async def dashboard():
    # Automatically secured — no Depends needed in the function signature
    return {"data": "protected content"}

@secure_router.get("/settings")
async def settings():
    return {"theme": "dark"}

app.include_router(secure_router)
```
