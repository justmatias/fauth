# Authorization (RBAC)

## Requiring Roles

```python
@app.get("/admin")
async def admin_panel(user: User = Depends(auth.require_roles(["admin"]))):
    return {"message": "Welcome, admin"}
```

Returns `403 Forbidden` with `{"detail": "Missing role: admin"}` if the user lacks the role.

## Requiring Permissions

```python
@app.get("/reports")
async def reports(user: User = Depends(auth.require_permissions(["read", "reports"]))):
    return {"data": "..."}
```

Returns `403 Forbidden` with `{"detail": "Insufficient permissions: requires read permission"}` if the user lacks any of the required permissions.

> **Note:** FAuth reads roles/permissions from `user.roles` and `user.permissions` attributes respectively. Make sure your user model exposes these fields.
