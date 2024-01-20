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

from datetime import datetime
from typing import Annotated
from typing import Any


from fastapi import Depends as FastAPIDependsFunc
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.params import Depends as FastAPIDependsClass
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError


READ = 0
WRITE = 1
DENY = -1


class PermissionError(HTTPException):
    """
    An HTTP exception you can raise in your own code to show errors to the client.

    Mainly for client errors, invalid authentication, invalid data, etc.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenError(HTTPException):
    """HTTP Exception you can raise to show on JWT token-related errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenBearer:
    """
    Parent class encapsulating JWT token obtaining and decode.

    Cannot be used as a FastAPI dependency, since the __call__ method returns None, but
    can be used as a parent class to create customized token procedures.
    """

    def __init__(
        self,
        token_key: str,
        secret_key: str,
        user_permissions_key: str | None = None,
        algorithms: str = "HS256",
    ):
        """
        _init__

        Parameters
        ----------
        token_key : str
            Name of the header or http cookie key where the token bearing user
            permissions is stored.
        secret_key : str
            Key used to decode the JWT token.
        user_permissions_key : str | None, optional
            Key name of the object specifying user permissions on the
            decoded JWT token, by default None
        algorithms : str, optional
            JWT token decode algorithm, by default "HS256"
        """
        self.token_key = token_key
        self.token_secret_key = secret_key
        self.algorithm = algorithms
        self.user_permissions_key = user_permissions_key

    def split_token_str(self, token: str, sep: str = " ") -> str:
        """Get only the token value from the source."""
        if "bearer" in token.lower():
            token = token.split(sep)[-1]

        return token

    def get_token_from_cookies(self, request: Request) -> str:
        """Read the token value from http cookies."""
        token = request.cookies.get(self.token_key)

        if not token:
            raise TokenError(
                status.HTTP_403_FORBIDDEN,
                f"Token not found on request cookies using key '{self.token_key}'",
            )

        return self.split_token_str(token)

    def get_token_from_header(self, request: Request) -> str:
        """Get the token value from request headers."""
        token = request.headers.get(self.token_key)

        if not token:
            raise TokenError(
                status.HTTP_403_FORBIDDEN,
                f"Token not found on request headers using key '{self.token_key}'",
            )

        return self.split_token_str(token)

    def decode_jwt(self, token: str) -> dict[str, int]:
        """Decode the retrieved token value and return the user permissions."""
        try:
            decoded_token = jwt.decode(
                token, self.token_secret_key, algorithms=self.algorithm
            )
        except ExpiredSignatureError:
            raise TokenError(
                status.HTTP_403_FORBIDDEN, "The token signature has expired."
            )
        except JWTClaimsError:
            raise TokenError(
                status.HTTP_403_FORBIDDEN, detail="The token claim is invalid."
            )
        except JWTError:  # generalist exception handler
            raise TokenError(
                status.HTTP_403_FORBIDDEN, "The token signature is invalid."
            )
        except Exception:  # even more generalist exception handler
            raise TokenError(status.HTTP_403_FORBIDDEN, "The token is invalid.")

        if self.user_permissions_key:
            try:
                return decoded_token[self.user_permissions_key]
            except KeyError:
                raise TokenError(
                    401,
                    (
                        "User permissions not found at token key "
                        f"'{self.user_permissions_key}'"
                    )
                )

        return decoded_token

    async def __call__(self) -> None:
        return None


class CookieTokenBearer(TokenBearer):
    """Read JWT token from http cookies."""

    async def __call__(self, request: Request) -> dict[str, Any]:
        """FastAPI FastAPIDependsFunc will call this method."""
        token = self.get_token_from_cookies(request)
        return self.decode_jwt(token)


class HTTPTokenBearer(TokenBearer):
    """Read JWT token from the request header"""

    async def __call__(self, request: Request) -> dict[str, Any]:
        """FastAPI FastAPIDependsFunc will call this method."""
        token = self.get_token_from_header(request)
        return self.decode_jwt(token)


class FlexibleTokenBearer(TokenBearer):
    """Tries to read the token from the cookies or from request headers."""

    async def __call__(self, request: Request) -> dict[str, Any]:
        """FastAPI FastAPIDependsFunc will call this method."""
        try:
            token = self.get_token_from_cookies(request)
        except TokenError:
            token = self.get_token_from_header(request)
        except Exception:
            raise TokenError(status.HTTP_417_EXPECTATION_FAILED, "Token not found.")

        return self.decode_jwt(token)


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
            if not self.area in claims:
                raise PermissionError(
                    status.HTTP_403_FORBIDDEN, f"'{self.area}' not in user permissions."
                )

            if not claims[self.area] >= self.level:
                raise PermissionError(
                    status.HTTP_403_FORBIDDEN,
                    "insufficient access level: "
                    f"({claims[self.area]}/{self.level}) on {self.area}.",
                )

        return check_user_permissions


def make_jwt_token(
    claims: dict[str, Any], secret: str, exp: datetime, algorithm: str = "HS256"
) -> str:
    """
    Create a JWT token.

    Parameters
    ----------
    claims : dict[str, Any]
        Token data.
    secret : str
        Secret key to sign the token.
    exp : datetime
        Token expiration datetime.
    algorithm : str, optional
        Encode algorithm, by default "HS256"

    Returns
    -------
    str
        Encoded JWT token.
    """
    to_encode = claims.copy()
    to_encode.update({"exp": exp})
    return jwt.encode(to_encode, key=secret, algorithm=algorithm)


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
    "PermissionError",
    "TokenError",
    "TokenBearer",
    "CookieTokenBearer",
    "HTTPTokenBearer",
    "FlexibleTokenBearer",
    "Rule",
    "make_rules",
]
