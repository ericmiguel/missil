"""JWT token obtaining via dependency injection."""

from abc import ABC
from abc import abstractmethod
from typing import Any

from fastapi import Request
from fastapi import status

from missil._deprecated import make_deprecated_getattr
from missil.codec import decode_jwt_token
from missil.exceptions import TokenValidationException


class TokenSource(ABC):
    """
    Abstract base for JWT token extraction and decoding.

    Not intended to be used directly as a FastAPI dependency. Subclass it
    to implement a custom token extraction strategy.
    """

    def __init__(
        self,
        token_key: str,
        secret_key: str,
        user_permissions_key: str,
        algorithms: str | list[str] = "HS256",
    ):
        """
        Configure JWT token extraction and decoding.

        Parameters
        ----------
        token_key : str
            Name of the header or cookie key that carries the JWT token.
        secret_key : str
            Secret key used to decode the signed token.
        user_permissions_key : str
            Key inside the decoded JWT payload that holds the permissions dict.
            Example payload:

            ```python
            {
                "username": "John Doe",
                "permissions": {  # user_permissions_key = "permissions"
                    "finances": 0,
                    "it": 1,
                },
            }
            ```

        algorithms : str | list[str], optional
            JWT decoding algorithm(s), by default "HS256".
            See python-jose docs for supported values.
        """
        if not user_permissions_key:
            raise ValueError(
                "user_permissions_key is required. "
                "Pass the JWT claim key that holds the permissions dict, "
                "e.g. TokenSource(..., user_permissions_key='userPermissions')."
            )
        self.token_key = token_key
        self.token_secret_key = secret_key
        self.algorithms: list[str] = (
            [algorithms] if isinstance(algorithms, str) else list(algorithms)
        )
        self.user_permissions_key = user_permissions_key

    def split_token_str(self, token: str, sep: str = " ") -> str:
        """Get only the token value from the source."""
        if "bearer" in token.lower():
            token = token.split(sep, 1)[-1]

        return token

    def get_token_from_cookies(self, request: Request) -> str:
        """Read the token value from http cookies."""
        token = request.cookies.get(self.token_key)

        if not token:
            raise TokenValidationException(
                status.HTTP_403_FORBIDDEN,
                f"Token not found on request cookies using key '{self.token_key}'",
            )

        return self.split_token_str(token)

    def get_token_from_header(self, request: Request) -> str:
        """Get the token value from request headers."""
        token = request.headers.get(self.token_key)

        if not token:
            raise TokenValidationException(
                status.HTTP_403_FORBIDDEN,
                f"Token not found on request headers using key '{self.token_key}'",
            )

        return self.split_token_str(token)

    def decode_jwt(self, token: str) -> dict[str, Any]:
        """Decode a retrieved token value and return the full JWT claims."""
        return decode_jwt_token(
            token, self.token_secret_key, algorithms=self.algorithms
        )

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
        try:
            user_permissions: dict[str, int] = decoded_token[self.user_permissions_key]
        except KeyError as ke:
            raise TokenValidationException(
                401,
                f"User permissions not found at token key "
                f"'{self.user_permissions_key}'",
            ) from ke
        return user_permissions

    @abstractmethod
    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """Resolve the JWT token from a request and return claims and permissions."""


class CookieTokenBearer(TokenSource):
    """Read JWT token from http cookies."""

    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """FastAPI will call this method when resolving the dependency."""
        decoded_token = self.decode_from_cookies(request)
        user_permissions = self.get_user_permissions(decoded_token)
        return decoded_token, user_permissions


class HeaderTokenBearer(TokenSource):
    """Read JWT token from the Authorization request header."""

    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """FastAPI will call this method when resolving the dependency."""
        decoded_token = self.decode_from_header(request)
        user_permissions = self.get_user_permissions(decoded_token)
        return decoded_token, user_permissions


class FallbackTokenBearer(TokenSource):
    """Try to read the token from cookies, falling back to the request header."""

    async def __call__(self, request: Request) -> tuple[dict[str, Any], dict[str, int]]:
        """FastAPI will call this method when resolving the dependency."""
        try:
            decoded_token = self.decode_from_cookies(request)
        except TokenValidationException:
            decoded_token = self.decode_from_header(request)

        user_permissions = self.get_user_permissions(decoded_token)
        return decoded_token, user_permissions


__getattr__ = make_deprecated_getattr(
    {
        "TokenBearer": "TokenSource",
        "HTTPTokenBearer": "HeaderTokenBearer",
        "FlexibleTokenBearer": "FallbackTokenBearer",
    },
    globals(),
    __name__,
)
