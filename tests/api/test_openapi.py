from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from fauth.providers import AuthProvider


def test_openapi_security_schemes(app: FastAPI) -> None:
    openapi_schema = app.openapi()
    assert "components" in openapi_schema
    assert "securitySchemes" in openapi_schema["components"]
    assert "OAuth2PasswordBearer" in openapi_schema["components"]["securitySchemes"]

    assert "/secure" in openapi_schema["paths"]
    assert "get" in openapi_schema["paths"]["/secure"]
    assert "security" in openapi_schema["paths"]["/secure"]["get"]
    assert {"OAuth2PasswordBearer": []} in openapi_schema["paths"]["/secure"]["get"][
        "security"
    ]


def test_auth_provider_get_security_scheme(provider: AuthProvider) -> None:
    scheme = provider.get_security_scheme()
    assert isinstance(scheme, OAuth2PasswordBearer)
