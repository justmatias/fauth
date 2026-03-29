from typing import Literal

from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    token_type: Literal["bearer"] = "bearer"
