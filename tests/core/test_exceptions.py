from fauth.core import FAuthError, InvalidTokenError, TokenExpiredError


def test_fauth_error() -> None:
    error = FAuthError("base error")
    assert isinstance(error, Exception)
    assert str(error) == "[FAuth] base error"


def test_token_expired_error() -> None:
    error = TokenExpiredError("token expired")
    assert isinstance(error, FAuthError)
    assert str(error) == "[FAuth] Token expired: token expired"


def test_invalid_token_error() -> None:
    error = InvalidTokenError("invalid token")
    assert isinstance(error, FAuthError)
    assert str(error) == "[FAuth] Invalid token: invalid token"
