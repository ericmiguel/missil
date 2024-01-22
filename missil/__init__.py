"""
Simple FastAPI declarative endpoint-level access control.

Scopes did not meet needs and other permission systems were too complex, so I designed
this code for my and my team needs, but feel free to use it if you like.

User permmissions declaration used by Missil follows the schema:

{
    'business area name': READ,
    'business area name': WRITE,
    'business area name 2': READ
    'business area name 2': WRITE
}
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
    """FastAPI dependency to set endpoint-level access rules."""

    def __init__(
        self,
        area: str,
        level: int,
        bearer: TokenBearer,
        use_cache: bool = True,
    ):
        """
        Set an area and access level to deny or allow user access to and endpoint.

        Parameters
        ----------
        area : str
            business area name like 'financial' or 'human resources'.
        level : int
            access level, like 'read', 'write', etc.
        bearer : TokenBearer
            JWT token source source.
        use_cache : bool, optional
            FastAPI Depends class parameter, by default True
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
    Create a missil rule set.

    A rule set is a simple dict[str, Rule] object. Each area will add a key to
    give a 'read' access and a second key to give 'write' access.

    This way, if you give a token source (TokenBearer subclass) and some business
    area names, like "it", "finances", "hr", this function will return something
    lile the following:

    rules = {
        'it:read': Rule,
        'it:write': Rule,
        'finances:read': Rule
        ...
    }

    So one can pass like a FastAPI dependency like

    @app.get("/items/{item_id}", dependencies=[rules["finances:read"]])
    def read_item(item_id: int, q: Union[str, None] = None):
        ...


    See the sample API in this repo to a working usage example.

    Parameters
    ----------
    bearer : TokenBearer
        _description_

    Returns
    -------
    dict[str, Rule]
        _description_
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
