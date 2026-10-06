from typing import Any

from fastapi import APIRouter, Depends

from fauth.providers import AuthProvider


class SecureAPIRouter(APIRouter):
    """
    An extension of FastAPI's APIRouter that automatically secures all its routes
    using the provided FAuth AuthProvider.
    """

    def __init__(
        self,
        auth_provider: AuthProvider[Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        dependencies: list[Any] = list(kwargs.pop("dependencies", []))

        # Add security scheme for OpenAPI documentation
        # and the user authentication dependency
        security_scheme = auth_provider.get_security_scheme()
        dependencies.extend((
            Depends(security_scheme),  # type: ignore[arg-type]
            Depends(auth_provider.require_active_user),
        ))

        kwargs["dependencies"] = dependencies

        super().__init__(*args, **kwargs)
