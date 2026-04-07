"""Missil core access control: AccessRule, Scope, and permission level constants."""

from collections.abc import Callable
from typing import Annotated
from typing import Any

from fastapi import Depends as FastAPIDependsFunc
from fastapi import status
from fastapi.params import Depends as FastAPIDependsClass

from missil._deprecated import make_deprecated_getattr
from missil.bearers import TokenSource
from missil.exceptions import PermissionDeniedException


READ = 0
WRITE = 1
DENY = -1  # reserved; raises NotImplementedError if used as an AccessRule level


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
        if level == DENY:
            raise NotImplementedError(
                "DENY rules are not yet implemented. "
                "Use PermissionDeniedException to block access unconditionally."
            )

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
                    dict[str, Any],  ## full claims
                    dict[str, int],  ## user permissions
                ],
                FastAPIDependsFunc(self.bearer),
            ],
        ) -> dict[str, Any]:
            """
            Run JWT claims against a declared endpoint rule.

            If claims contains the requested business area and a sufficient
            access level, the endpoint is accessible and the full claims are
            returned.

            Parameters
            ----------
            claims : Annotated[tuple[dict[str, Any], dict[str, int]], ...]
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


class Scope:
    """
    Business area grouping READ and WRITE access rules.

    A Scope instance holds pre-built AccessRule objects for each access level,
    ready to be injected as FastAPI endpoint dependencies:

    ```python
    bearer = ...
    finances = Scope("finances", bearer)


    @app.get("/finances/read", dependencies=[finances.READ])
    def finances_read() -> dict[str, str]: ...
    ```
    """

    def __init__(self, name: str, bearer: TokenSource) -> None:
        """
        Create a business area scope.

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


def make_scopes(bearer: TokenSource, *areas: str) -> dict[str, Scope]:
    """
    Create a Missil ruleset from a token source and business area names.

    Returns a dict mapping each area name to a :class:`Scope` with ready-to-use
    READ and WRITE :class:`AccessRule` dependencies:

    ```python
    rules = make_scopes(bearer, "finances", "it", "hr")


    @app.get("/finances", dependencies=[rules["finances"].READ])
    def read_finances(): ...
    ```

    Parameters
    ----------
    bearer : TokenSource
        JWT token source. See Bearers module.
    *areas : str
        Business area names to protect.

    Returns
    -------
    dict[str, Scope]
        Mapping of area name to Scope.
    """
    return {area: Scope(area, bearer) for area in areas}


def make_scope(bearer: TokenSource, area: str) -> Scope:
    """
    Create a single business area Scope.

    Parameters
    ----------
    bearer : TokenSource
        JWT token source. See Bearers module.
    area : str
        Business area name.

    Returns
    -------
    Scope
        Business area scope with READ and WRITE rules.
    """
    return Scope(area, bearer)


__getattr__ = make_deprecated_getattr(
    {
        "Rule": "AccessRule",
        "Area": "Scope",
        "make_rule": "make_scope",
        "make_rules": "make_scopes",
    },
    globals(),
    __name__,
)
