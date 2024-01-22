"""
Simple FastAPI declarative endpoint-level access control.
"""

from typing import Annotated

from fastapi import Depends as FastAPIDependsFunc
from fastapi import status
from fastapi.params import Depends as FastAPIDependsClass

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
DENY = -1


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
            Business area name like 'financial' or 'human resources'.
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
    def dependency(self):
        """Allows Missil to pass a FastAPI dependency that gets correctly evaluated."""

        def check_user_permissions(
            claims: Annotated[dict[str, int], FastAPIDependsFunc(self.bearer)]
        ):
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


def make_rules(bearer: TokenBearer, *areas) -> dict[str, Rule]:
    """
    Create a Missil ruleset, conveniently.

    A ruleset is a simple dict bearing endpoint-appliable rules (dict[str, Rule].

    Given a token source (see Bearers module) and some business
    area names, like "it", "finances", "hr", this function will return something
    lile the following:

    ```python
    {
        'it:read': Rule,
        'it:write': Rule,
        'finances:read': Rule
        ...
    }
    ```

    So, one can pass like a FastAPI dependency like:

    ```python
    @app.get("/items/{item_id}", dependencies=[rules["finances:read"]])
    def read_item(item_id: int, q: Union[str, None] = None):
        ...
    ```

    See the sample API (sample/main.py) to a working usage example.

    Parameters
    ----------
    bearer : TokenBearer
        JWT token source source. See Bearers module.

    Returns
    -------
    dict[str, Rule]
        Dict containing endpoint-appliable rules.
    """
    rules = {}
    for level in [READ, WRITE]:
        for area in areas:
            level_name = "read" if level <= 0 else "write"
            rules.update({f"{area}:{level_name}": Rule(area, level, bearer)})

    return rules


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
]
