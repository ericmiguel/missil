"""Missil routers, just like FastAPI routers."""

from collections.abc import Callable
from collections.abc import Sequence
from enum import Enum
from typing import Any

from fastapi import APIRouter
from fastapi.params import Depends as FastAPIDependsClass
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp
from starlette.types import Lifespan

from missil.rules import Rule


class QualifiedRouter(APIRouter):
    """Fastapi router with rules parameter."""

    def __init__(
        self,
        *,
        prefix: str = "",
        rules: Sequence[Rule],
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
        Same parameters as in FastAPI APIRouter class, plus an extra rules parameter.

        It can be used to avoid multiple redudant rule declarations in same
        business area endpoints.

        Example:

        ```python
        ba = missil.make_rules(bearer, "finances")  # business area
        sample_rule_router = missil.QualifiedRouter(rules=[ba["finances"].READ])
        ```

        All other original parameters are explicit declared to allow autocomplete and
        intellisense-like code editor capabilities. They are exactly the same as in
        FastAPI APIrouter class.

        Parameters
        ----------
        rules : Sequence[Rule]
            Sequence of Missil rule objects.
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
