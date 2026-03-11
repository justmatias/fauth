from dataclasses import dataclass


@dataclass
class FAuthError(Exception):
    message: str

    def __str__(self) -> str:
        return f"[FAuth] {self.message}"


class InvalidTokenError(FAuthError):
    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid token: {message}")


class TokenExpiredError(FAuthError):
    def __init__(self, message: str) -> None:
        super().__init__(f"Token expired: {message}")
