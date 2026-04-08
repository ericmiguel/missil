"""Missil type definitions for JWT claims."""

from typing import TypedDict


class JWTClaims(TypedDict, total=False):
    """
    Base TypedDict for JWT claim payloads (RFC 7519).

    All standard JWT registered claims are declared as optional fields.
    Subclass this to add application-specific claims with full type-checker
    support while remaining a plain :class:`dict` at runtime.

    Attributes
    ----------
    exp : int
        Expiration time — Unix timestamp after which the token is invalid.
        Validated automatically by PyJWT on decode.
    iat : int
        Issued at — Unix timestamp of when the token was issued.
    nbf : int
        Not before — Unix timestamp before which the token is not valid.
        Validated automatically by PyJWT on decode.
    sub : str
        Subject — identifier of the token's subject (e.g. user ID).
    iss : str
        Issuer — identifies who issued the token (e.g. ``"myapp.com"``).
    aud : str | list[str]
        Audience — identifies the recipients the token is intended for.
    jti : str
        JWT ID — unique identifier for the token, useful for revocation.

    Examples
    --------
    The field holding user permissions must match the ``permissions_key``
    configured on the bearer instance:

    ```python
    bearer = missil.TokenBearer(TOKEN_KEY, SECRET_KEY, permissions_key="scopes")
    ```

    Declare a subclass with a field of the same name:

    ```python
    from missil import JWTClaims


    class AppClaims(JWTClaims):
        username: str
        scopes: dict[str, int]  # must match permissions_key
    ```

    Then annotate route parameters with the subclass:

    ```python
    @app.get("/profile", dependencies=[areas.finances.READ])
    def profile(user: Annotated[AppClaims, areas.finances.READ]) -> AppClaims:
        username = user["username"]  # typed as str
        return user
    ```
    """

    exp: int
    iat: int
    nbf: int
    sub: str
    iss: str
    aud: str | list[str]
    jti: str
