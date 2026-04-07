"""Missil routers, just like FastAPI routers."""

from collections.abc import Callable
from collections.abc import Sequence
from enum import Enum
from typing import Any
import warnings

from fastapi import APIRouter
from fastapi.params import Depends as FastAPIDependsClass
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp
from starlette.types import Lifespan

from missil.rules import AccessRule


class ProtectedRouter(APIRouter):
    """FastAPI router with built-in access rules applied to all its routes."""

    def __init__(
        self,
        *,
        prefix: str = "",
        rules: Sequence[AccessRule],
        tags: list[str | Enum] | None = None,
        dependencies: Sequence[FastAPIDependsClass] | None = None,
        default_response_class: type[Response] = JSONResponse,
        responses: dict[int | str, dict[str, Any]] | None = None,
        callbacks: list[BaseRoute] | None = None,
        routes: list[BaseRoute] | None = None,
        redirect_slashes: bool = True,
        default: ASGIApp | None = None,
        dependency_overrides_provider: Any | None = None,
        route_class: type[APIRoute] = APIRoute,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
        lifespan: Lifespan[Any] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
    ) -> None:
        """
        FastAPI APIRouter with a mandatory access rules parameter.

        All routes added to this router automatically require the declared rules,
        avoiding repetition across endpoints that share the same access policy.

        Example:

        ```python
        scopes = missil.make_scopes(bearer, "finances")
        router = missil.ProtectedRouter(rules=[scopes["finances"].READ])
        ```

        All other parameters are identical to FastAPI's APIRouter.

        Parameters
        ----------
        rules : Sequence[AccessRule]
            One or more Missil AccessRule objects to enforce on every route.
        """
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )

        self.dependencies += rules


_DEPRECATED: dict[str, str] = {
    "QualifiedRouter": "ProtectedRouter",
}


def __getattr__(name: str) -> object:
    if name in _DEPRECATED:
        new_name = _DEPRECATED[name]
        warnings.warn(
            f"'{name}' is deprecated and will be removed in a future version. "
            f"Use '{new_name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
