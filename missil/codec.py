"""JWT token encoding and decoding."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any

from fastapi import status
import jwt as pyjwt

from missil.exceptions import TokenValidationException


def decode_jwt_token(
    token: str, secret_key: str, algorithms: str | list[str] = "HS256"
) -> dict[str, Any]:
    """
    Decode a JWT token using PyJWT.

    Parameters
    ----------
    token : str
        Token to be decoded.
    secret_key : str
        Secret key to decode the signed token.
    algorithms : str | list[str]
        Decoding algorithm(s). See PyJWT docs for more details.

    Returns
    -------
    dict[str, Any]
        Decoded claims.

    Raises
    ------
    TokenValidationException
        The token signature has expired.
    TokenValidationException
        The token signature or claims are invalid.
    """
    algs: list[str] = [algorithms] if isinstance(algorithms, str) else list(algorithms)
    try:
        return pyjwt.decode(token, secret_key, algorithms=algs)
    except pyjwt.ExpiredSignatureError as e:
        raise TokenValidationException(
            status.HTTP_403_FORBIDDEN, "The token signature has expired."
        ) from e
    except pyjwt.DecodeError as e:
        raise TokenValidationException(
            status.HTTP_403_FORBIDDEN, "The token signature is invalid."
        ) from e
    except pyjwt.PyJWTError as e:
        raise TokenValidationException(
            status.HTTP_403_FORBIDDEN, "The token is invalid."
        ) from e


def encode_jwt_token(
    claims: dict[str, Any],
    secret: str,
    exp: int,
    base: datetime | None = None,
    algorithm: str = "HS256",
) -> str:
    """
    Create a JWT token.

    Parameters
    ----------
    claims : dict[str, Any]
        Token user data.
    secret : str
        Secret key to sign the token.
    exp : int
        Token expiration in hours.
    base : datetime, optional
        Token expiration base datetime, where the final datetime is given by
        base + exp, by default datetime.now(timezone.utc)
    algorithm : str, optional
        Encode algorithm, by default "HS256"

    Returns
    -------
    str
        Encoded JWT token string.
    """
    if base is None:
        base = datetime.now(timezone.utc)

    to_encode = claims.copy()
    to_encode.update({"exp": base + timedelta(hours=exp)})
    return pyjwt.encode(to_encode, key=secret, algorithm=algorithm)
