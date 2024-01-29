"""Simple FastAPI declarative endpoint-level access control."""

from collections.abc import Callable
from collections.abc import Sequence
from enum import Enum
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends as FastAPIDependsFunc
from fastapi import status
from fastapi.params import Depends as FastAPIDependsClass
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp
from starlette.types import Lifespan

from missil.bearers import CookieTokenBearer
from missil.bearers import FlexibleTokenBearer
from missil.bearers import HTTPTokenBearer
from missil.bearers import TokenBearer
from missil.exceptions import PermissionErrorException
from missil.exceptions import TokenErrorException
from missil.jwt_utilities import decode_jwt_token
from missil.jwt_utilities import encode_jwt_token


READ = 0
WRITE = 1
DENY = -1  # TODO: will overlap READ and WRITE permissions, but not implemented yet


class Rule(FastAPIDependsClass):
    """FastAPI dependency to set and endpoint-level access rule."""

    def __init__(
        self,
        area: str,
        level: int,
        bearer: TokenBearer,
        use_cache: bool = True,
    ):
        """
        Grant or deny user access to an endpoint.

        Access is granted through the verification of the business area and
        verification of the access level expressed in the jwt token captured by
        the declared TokenBearer object.

        Parameters
        ----------
        area : str
            Business area name, like 'financial' or 'human resources'.
        level : int
            Access level: READ = 0 / WRITE = 1.
        bearer : TokenBearer
            JWT token source source. See Bearers module.
        use_cache : bool, optional
            FastAPI Depends class parameter, by default True.
        """
        self.area = area
        self.level = level
        self.bearer = bearer
        self.use_cache = use_cache

    @property
    def dependency(self) -> Callable[..., Any] | None:
        """Allows Missil to pass a FastAPI dependency that gets correctly evaluated."""

        def check_user_permissions(
            claims: Annotated[dict[str, int], FastAPIDependsFunc(self.bearer)]
        ) -> None:
            """
            Run JWT claims against an declared endpoint rule.

            If claims contains the asked business area and sufficient access level,
            the endpoint access is granted to the user.

            Parameters
            ----------
            claims : Annotated[dict[str, int], FastAPIDependsFunc
                Content decoded from a JWT Token, obtained after FastAPI resolves
                the TokenBearer dependency. Missil expects an dict using the
                following structure:

                ```python
                {
                    'business area name': READ,
                    'business area name': WRITE,
                    'business area name 2': READ
                    'business area name 2': WRITE
                }
                ```

            Raises
            ------
            PermissionErrorException
                Business area not listed on claims.
            PermissionErrorException
                Insufficient access level.
            """
            if self.area not in claims:
                raise PermissionErrorException(
                    status.HTTP_403_FORBIDDEN, f"'{self.area}' not in user permissions."
                )

            if not claims[self.area] >= self.level:
                raise PermissionErrorException(
                    status.HTTP_403_FORBIDDEN,
                    "insufficient access level: "
                    f"({claims[self.area]}/{self.level}) on {self.area}.",
                )

        return check_user_permissions

    if TYPE_CHECKING:

        @dependency.setter
        def dependency(self, _: Any) -> None:
            """
            Only declared to avoid type checking errors.

            Mypy: cannot override writeable attribute with read-only property.
            """
            pass


class Area:
    """
    Business area.

    A business area instance holds up READ and WRITE rules as attributes, which
    can be injected as a FastAPI endpoint dependency. For example:

    ```python
    bearer = ...
    finances = Area('finances', bearer)

    @app.get("/finances/read", dependencies=[finances.READ])
    def finances_read() -> dict[str, str]:
        ...
    ```
    """

    def __init__(self, name: str, bearer: TokenBearer) -> None:
        """
        Creates a business area object.

        Parameters
        ----------
        name : str
            Business area name.
        bearer : TokenBearer
            JWT token source source. See Bearers module.
        """
        self.name: str = name
        self.bearer = bearer
        self.READ = Rule(self.name, 0, self.bearer)
        self.WRITE = Rule(self.name, 1, self.bearer)


def make_rules(bearer: TokenBearer, *areas: str) -> dict[str, Area]:
    """
    Create a Missil ruleset, conveniently.

    A ruleset is a simple mapping bearing endpoint-appliable rule
    bearers

    ```python
    rules: dict[str, Area] = make_rules(..., ...).
    ```

    Given a token source (see Bearers module) and some business
    area names, like "it", "finances", "hr", this function will return something
    lile the following:

    ```python
    {
        'it': Area,
        'finances': Area,
        'hr': Area
        ...
    }
    ```

    So, one can pass like a FastAPI dependency, as shown in the following example:

    ```python
    @app.get("/items/{item_id}", dependencies=[rules["finances"].READ])
    def read_item(item_id: int, q: Union[str, None] = None):
        ...
    ```

    See the sample API (sample/main.py) to a folly working usage example.

    Parameters
    ----------
    bearer : TokenBearer
        JWT token source source. See Bearers module.

    Returns
    -------
    dict[str, Area]
        Dict containing endpoint-appliable rules.
    """
    return {area: Area(area, bearer) for area in areas}


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


__all__ = [
    "PermissionErrorException",
    "TokenErrorException",
    "TokenBearer",
    "encode_jwt_token",
    "decode_jwt_token",
    "CookieTokenBearer",
    "HTTPTokenBearer",
    "FlexibleTokenBearer",
    "Rule",
    "make_rules",
    "QualifiedRouter",
]
