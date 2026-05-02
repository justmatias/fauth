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

> **Field names:** By default, FAuth reads roles from `user.roles` and permissions from `user.permissions`. If your model uses different field names, pass `roles_field_name` or `permissions_field_name` to `AuthProvider` (e.g., `roles_field_name="groups", permissions_field_name="scopes"`).
