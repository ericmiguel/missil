"""Missil core access control: AccessRule, Area, AreasBase, Role, permissions."""

from collections.abc import Callable
import inspect
from typing import Annotated
from typing import Any
from typing import get_type_hints
import warnings

from fastapi import Depends as FastAPIDependsFunc
from fastapi import status
from fastapi.params import Depends as FastAPIDependsClass

from missil._deprecated import make_deprecated_getattr
from missil.bearers import TokenSource
from missil.exceptions import PermissionDeniedException
from missil.types import JWTClaims


READ = 0
WRITE = 1
ADMIN = 2


class AccessRule(FastAPIDependsClass):
    """FastAPI dependency that enforces an endpoint-level access rule."""

    area: str
    level: int
    bearer: TokenSource

    def __init__(
        self,
        area: str,
        level: int,
        bearer: TokenSource,
        use_cache: bool = True,
    ):
        """
        Grant or deny user access to an endpoint.

        Access is granted by verifying that the JWT token claims include
        the requested business area at the required access level.

        Parameters
        ----------
        area : str
            Business area name, e.g. 'finances' or 'human_resources'.
        level : int
            Required access level: READ = 0 / WRITE = 1.
        bearer : TokenSource
            JWT token source. See Bearers module.
        use_cache : bool, optional
            FastAPI Depends cache parameter, by default True.
        """
        # FastAPIDependsClass became a frozen dataclass in FastAPI 0.115+;
        # object.__setattr__ is the standard way to set fields on frozen instances.
        # Note: "dependency" is intentionally not set here — it's provided by the
        # property below. "scope" uses the dataclass default (None).
        object.__setattr__(self, "area", area)
        object.__setattr__(self, "level", level)
        object.__setattr__(self, "bearer", bearer)
        object.__setattr__(self, "use_cache", use_cache)
        object.__setattr__(self, "scope", None)
        object.__setattr__(self, "dependency", self._make_dependency())

    def _make_dependency(self) -> Callable[..., Any]:
        """Build the FastAPI-injectable permission-checking callable."""

        def check_user_permissions(
            claims: Annotated[
                tuple[
                    JWTClaims,  ## full claims
                    dict[str, int],  ## user permissions
                ],
                FastAPIDependsFunc(self.bearer),
            ],
        ) -> JWTClaims:
            """
            Run JWT claims against a declared endpoint rule.

            If claims contains the requested business area and a sufficient
            access level, the endpoint is accessible and the full claims are
            returned.

            Parameters
            ----------
            claims : Annotated[tuple[JWTClaims, dict[str, int]], ...]
                Decoded JWT content obtained after FastAPI resolves the TokenSource dep.

            Raises
            ------
            PermissionDeniedException
                Business area not listed on claims.
            PermissionDeniedException
                Insufficient access level.
            """
            if self.area not in claims[1]:
                raise PermissionDeniedException(
                    status.HTTP_403_FORBIDDEN, f"'{self.area}' not in user permissions."
                )

            if not claims[1][self.area] >= self.level:
                raise PermissionDeniedException(
                    status.HTTP_403_FORBIDDEN,
                    "insufficient access level: "
                    f"({claims[1][self.area]}/{self.level}) on {self.area}.",
                )

            return claims[0]

        return check_user_permissions


class Area:
    """
    Business area grouping READ and WRITE access rules.

    An Area instance holds pre-built AccessRule objects for each access level,
    ready to be injected as FastAPI endpoint dependencies:

    ```python
    bearer = ...
    finances = Area("finances", bearer)


    @app.get("/finances/read", dependencies=[finances.READ])
    def finances_read() -> dict[str, str]: ...
    ```
    """

    def __init__(self, name: str, bearer: TokenSource) -> None:
        """
        Create a business area.

        Parameters
        ----------
        name : str
            Business area name.
        bearer : TokenSource
            JWT token source. See Bearers module.
        """
        self.name: str = name
        self.bearer = bearer
        self.READ = AccessRule(self.name, READ, self.bearer)
        self.WRITE = AccessRule(self.name, WRITE, self.bearer)
        self.ADMIN = AccessRule(self.name, ADMIN, self.bearer)


class AreasBase:
    """
    Base class for declaring business areas as typed attributes.

    Subclass it and annotate each field as :class:`Area`. On instantiation,
    all annotated fields are automatically created and accessible as typed
    attributes:

    ```python
    import missil

    bearer = missil.TokenBearer("Authorization", SECRET_KEY, "permissions")


    class AppAreas(missil.AreasBase):
        finances: missil.Area
        it: missil.Area


    areas = AppAreas(bearer)


    @app.get("/report", dependencies=[areas.finances.READ])
    def report(): ...
    ```

    Annotations typed as anything other than :class:`Area` are silently ignored,
    so you can freely add non-area class attributes to your subclass.
    """

    def __init__(self, bearer: TokenSource) -> None:
        """
        Instantiate all declared Area fields.

        Parameters
        ----------
        bearer : TokenSource
            JWT token source shared by all areas in this group.
        """
        try:
            hints = get_type_hints(type(self))
        except Exception:
            hints = getattr(type(self), "__annotations__", {})

        for name, annotation in hints.items():
            if annotation is Area:
                setattr(self, name, Area(name, bearer))


class Role(FastAPIDependsClass):
    """
    A named group of AccessRules that must all be satisfied for access to be granted.

    Use a Role to avoid repeating the same set of rules across multiple endpoints.
    Access is granted only when every constituent AccessRule passes:

    ```python
    bearer = missil.TokenBearer("Authorization", SECRET_KEY, "permissions")


    class AppAreas(missil.AreasBase):
        finances: missil.Area
        it: missil.Area


    areas = AppAreas(bearer)

    analyst = missil.Role(areas.finances.READ, areas.it.READ)


    @app.get("/dashboard", dependencies=[analyst])
    def dashboard(): ...
    ```

    If any rule fails, FastAPI raises HTTP 403 before the endpoint is reached.
    """

    rules: tuple["AccessRule", ...]

    def __init__(self, *rules: "AccessRule", use_cache: bool = True) -> None:
        """
        Create a role from one or more AccessRules.

        Parameters
        ----------
        *rules : AccessRule
            The access rules that must all pass for this role to be satisfied.
        use_cache : bool, optional
            FastAPI Depends cache parameter, by default True.
        """
        object.__setattr__(self, "rules", rules)
        object.__setattr__(self, "use_cache", use_cache)
        object.__setattr__(self, "scope", None)
        object.__setattr__(self, "dependency", self._make_dependency())

    def _make_dependency(self) -> Callable[..., Any]:
        """Build the FastAPI-injectable callable that enforces all constituent rules."""
        rules = self.rules

        params = [
            inspect.Parameter(
                f"_rule_{i}",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=FastAPIDependsFunc(rule.dependency),
                annotation=JWTClaims,
            )
            for i, rule in enumerate(rules)
        ]

        def check_role(**kwargs: JWTClaims) -> JWTClaims:
            """Enforce all role rules; return claims from the first resolved rule."""
            return next(iter(kwargs.values()))

        check_role.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]

        return check_role


def make_areas(bearer: TokenSource, *areas: str) -> dict[str, Area]:
    """
    Create a Missil ruleset from a token source and business area names.

    !!! danger "Deprecated"
        Use `AreasBase` instead:

        ```python
        class AppAreas(missil.AreasBase):
            finances: missil.Area
            it: missil.Area


        areas = AppAreas(bearer)
        ```

    Parameters
    ----------
    bearer : TokenSource
        JWT token source. See Bearers module.
    *areas : str
        Business area names to protect.

    Returns
    -------
    dict[str, Area]
        Mapping of area name to Area.
    """
    warnings.warn(
        "make_areas() is deprecated and will be removed in a future version. "
        "Use AreasBase instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return {area: Area(area, bearer) for area in areas}


def make_area(bearer: TokenSource, area: str) -> Area:
    """
    Create a single business area.

    !!! danger "Deprecated"
        Use `Area` directly instead:

        ```python
        finances = missil.Area("finances", bearer)
        ```

    Parameters
    ----------
    bearer : TokenSource
        JWT token source. See Bearers module.
    area : str
        Business area name.

    Returns
    -------
    Area
        Business area with READ and WRITE rules.
    """
    warnings.warn(
        "make_area() is deprecated and will be removed in a future version. "
        "Use Area(name, bearer) directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Area(area, bearer)


__getattr__ = make_deprecated_getattr(
    {
        "Rule": "AccessRule",
        "Scope": "Area",
        "make_scope": "make_area",
        "make_scopes": "make_areas",
        "make_rule": "make_area",
        "make_rules": "make_areas",
    },
    globals(),
    __name__,
)
