from pydantic import BaseModel, Field


class FieldNames(BaseModel):
    password: str = Field(
        default="hashed_password",
        description="Attribute on the user model holding the hashed password",
    )
    roles: str = Field(
        default="roles",
        description="Attribute on the user model holding the list of roles",
    )
    permissions: str = Field(
        default="permissions",
        description="Attribute on the user model holding the list of permissions",
    )
    active_status: str = Field(
        default="is_active",
        description="Attribute on the user model indicating whether the user is active",
    )
