"""JWT token obtaining via dependency injection."""

from typing import Any

from fastapi import Request
from fastapi import status

from missil.exceptions import TokenErrorException
from missil.jwt_utilities import decode_jwt_token


class TokenBearer:
    """
    Parent class encapsulating JWT token obtaining and decoding.

    Shouldn't be used as a FastAPI dependency, since the __call__ method returns None
    (and is herefore declared just to avoid code checking alerts), but can be used as
    a parent class to create customized token procedures.
    """

    def __init__(
        self,
        token_key: str,
        secret_key: str,
        user_permissions_key: str | None = None,
        algorithms: str = "HS256",
    ):
        """
        JWT token obtaining and decoding.

        Parameters
        ----------
        token_key : str
            Name of the header or http cookie key where the token bearing user
            permissions is stored.
        secret_key : str
            Key used to decode the JWT token. See Python-jose docs for more details.
        user_permissions_key : str | None, optional
            Key name of the object specifying user permissions on the
            decoded JWT token, by default None. Example:

            Supposing the following decoded token claim:
            ```python
            {
                "username": "John Doe",
                "permissions": {  # user_permissions_key
                    "finances": 0,
                    "it": 0,
                },
            }
            ```

        algorithms : str, optional
            JWT token decode algorithm, by default "HS256". See Python-jose docs
            for more details.
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
        """Decode a retrieved token value and return the user permissions."""
        decoded_token = decode_jwt_token(
            token, self.token_secret_key, algorithm=self.algorithm
        )
        return decoded_token

    def decode_from_cookies(self, request: Request) -> dict[str, Any]:
        """Get token from cookies and decode it."""
        token = self.get_token_from_cookies(request)
        return self.decode_jwt(token)

    def decode_from_header(self, request: Request) -> dict[str, Any]:
        """Get token from headers and decode it."""
        token = self.get_token_from_header(request)
        return self.decode_jwt(token)

    def get_user_permissions(self, decoded_token: dict[str, Any]) -> dict[str, int]:
        """Get user permissions from a decoded token."""
        if self.user_permissions_key:
            try:
                user_permissions: dict[str, int] = decoded_token[
                    self.user_permissions_key
                ]
            except KeyError as ke:
                raise TokenErrorException(
                    401,
                    (
                        "User permissions not found at token key "
                        f"'{self.user_permissions_key}'"
                    ),
                ) from ke
            else:
                return user_permissions

        raise TokenErrorException(500, "User permissions key not provided.")


class CookieTokenBearer(TokenBearer):
    """Read JWT token from http cookies."""

    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """Fastapi FastAPIDependsFunc will call this method."""
        decoded_token = self.decode_from_cookies(request)
        user_permissions = self.get_user_permissions(decoded_token)
        return decoded_token, user_permissions


class HTTPTokenBearer(TokenBearer):
    """Read JWT token from the request header."""

    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """Fastapi FastAPIDependsFunc will call this method."""
        decoded_token = self.decode_from_header(request)
        user_permissions = self.get_user_permissions(decoded_token)
        return decoded_token, user_permissions


class FlexibleTokenBearer(TokenBearer):
    """Tries to read the token from the cookies or from request headers."""

    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """Fastapi FastAPIDependsFunc will call this method."""
        try:
            decoded_token = self.decode_from_cookies(request)
        except TokenErrorException:
            decoded_token = self.decode_from_header(request)
        except Exception as e:
            raise TokenErrorException(
                status.HTTP_417_EXPECTATION_FAILED, "Token not found."
            ) from e

        user_permissions = self.get_user_permissions(decoded_token)
        return decoded_token, user_permissions
