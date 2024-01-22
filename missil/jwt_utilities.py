from datetime import datetime
from typing import Any

from fastapi import status
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError

from missil.exceptions import TokenErrorException


def decode_jwt_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=algorithm)
    except ExpiredSignatureError:
        raise TokenErrorException(
            status.HTTP_403_FORBIDDEN, "The token signature has expired."
        )
    except JWTClaimsError:
        raise TokenErrorException(
            status.HTTP_403_FORBIDDEN, detail="The token claim is invalid."
        )
    except JWTError:  # generalist exception handler
        raise TokenErrorException(
            status.HTTP_403_FORBIDDEN, "The token signature is invalid."
        )
    except Exception:  # even more generalist exception handler
        raise TokenErrorException(status.HTTP_403_FORBIDDEN, "The token is invalid.")

    return decoded_token


def encode_jwt_token(
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
