from typing import Any

from fastapi import Request
from fastapi import status

from missil.exceptions import TokenErrorException
from missil.jwt_utilities import decode_jwt_token


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
            raise TokenErrorException(
                status.HTTP_403_FORBIDDEN,
                f"Token not found on request cookies using key '{self.token_key}'",
            )

        return self.split_token_str(token)

    def get_token_from_header(self, request: Request) -> str:
        """Get the token value from request headers."""
        token = request.headers.get(self.token_key)

        if not token:
            raise TokenErrorException(
                status.HTTP_403_FORBIDDEN,
                f"Token not found on request headers using key '{self.token_key}'",
            )

        return self.split_token_str(token)

    def decode_jwt(self, token: str) -> dict[str, int]:
        """Decode the retrieved token value and return the user permissions."""

        decoded_token = decode_jwt_token(
            token, self.token_secret_key, algorithm=self.algorithm
        )

        if self.user_permissions_key:
            try:
                return decoded_token[self.user_permissions_key]
            except KeyError:
                raise TokenErrorException(
                    401,
                    (
                        "User permissions not found at token key "
                        f"'{self.user_permissions_key}'"
                    ),
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
        except TokenErrorException:
            token = self.get_token_from_header(request)
        except Exception:
            raise TokenErrorException(
                status.HTTP_417_EXPECTATION_FAILED, "Token not found."
            )

        return self.decode_jwt(token)
