from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""

    model_config = ConfigDict(extra="allow")

    sub: str
    exp: int
    iat: int
    jti: str
    scopes: list[str] = Field(default_factory=list)
    token_type: Literal["access", "refresh", "password_reset", "email_verification"]


class TokenResponse(BaseModel):
    """Response returned upon successful authentication or token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
