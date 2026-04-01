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
        dependencies.append(Depends(auth_provider.require_active_user))
        kwargs["dependencies"] = dependencies

        super().__init__(*args, **kwargs)
