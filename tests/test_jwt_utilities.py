from missil import jwt_utilities
from missil.exceptions import TokenErrorException
from datetime import datetime
import logging
import pytest
import warnings
from jose import jwt

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def secret_key():
    return "b522178515f3a13879e6ef63d40d18fbbffd4ff29673fcf442a6eca264a2ee16"


@pytest.fixture(scope="module")
def fake_secret_key():
    return "da_secret"


@pytest.fixture(scope="module")
def claims():
    return {
        "username": "johndoe",
        "permissions": {
            "finances": 1,
            "human_resources": 0,
        },
    }


@pytest.fixture(scope="module")
def fake_claims():
    return {
        "username": "johndoe",
        "permissions": {
            "finances": 1,
            "human_resources": 1,
        },
    }


@pytest.fixture(scope="module")
def token_valid_expiration():
    return datetime(2200, 1, 1, 0, 0, 0, 0)


@pytest.fixture(scope="module")
def token_expired_datetime():
    return datetime(1900, 1, 1, 0, 0, 0, 0)


@pytest.fixture(scope="module")
def token_invalid_expiration():
    return "a_string"


@pytest.fixture(scope="module")
def encoded_jwt_token(claims, secret_key, token_valid_expiration):
    to_encode = claims.copy()
    to_encode.update({"exp": token_valid_expiration})
    return jwt.encode(to_encode, secret_key, "HS256")


@pytest.fixture(scope="module")
def encoded_invalid_claims_jwt_token(claims, secret_key, token_invalid_expiration):
    to_encode = claims.copy()
    to_encode.update({"exp": token_invalid_expiration})
    return jwt.encode(to_encode, secret_key, "HS256")


@pytest.fixture(scope="module")
def encoded_expired_jwt_token(claims, secret_key, token_expired_datetime):
    to_encode = claims.copy()
    to_encode.update({"exp": token_expired_datetime})
    return jwt.encode(to_encode, secret_key, "HS256")


@pytest.fixture(scope="module")
def encoded_invalid_jwt_token(claims, secret_key, token_expired_datetime):
    to_encode = claims.copy()
    to_encode.update({"exp": token_expired_datetime})
    encoded = jwt.encode(to_encode, secret_key, "HS256")
    invalidated_token = encoded[:39] + encoded[40:]
    return invalidated_token


def test_encode_jwt_token(
    claims, secret_key, token_valid_expiration, encoded_jwt_token
):
    result = jwt_utilities.encode_jwt_token(claims, secret_key, token_valid_expiration)
    assert result == encoded_jwt_token


def test_encode_expired_jwt_token(
    claims, secret_key, token_expired_datetime, encoded_jwt_token
):
    result = jwt_utilities.encode_jwt_token(claims, secret_key, token_expired_datetime)
    assert result != encoded_jwt_token


def test_encode_fake_claim_jwt_token(
    fake_claims, secret_key, token_valid_expiration, encoded_jwt_token
):
    result = jwt_utilities.encode_jwt_token(
        fake_claims, secret_key, token_valid_expiration
    )
    assert result != encoded_jwt_token


def test_encode_jwt_token_fake_key(
    claims, fake_secret_key, token_valid_expiration, encoded_jwt_token
):
    result = jwt_utilities.encode_jwt_token(
        claims, fake_secret_key, token_valid_expiration
    )
    assert result != encoded_jwt_token


def test_decode_jwt_token(claims, secret_key, encoded_jwt_token):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        result = jwt_utilities.decode_jwt_token(encoded_jwt_token, secret_key)
    del result["exp"]
    assert result == claims


def test_decode_jwt_token_invalid_signature(fake_secret_key, encoded_jwt_token):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        with pytest.raises(
            TokenErrorException, match="The token signature is invalid."
        ):
            jwt_utilities.decode_jwt_token(encoded_jwt_token, fake_secret_key)


def test_decode_jwt_invalid_claim(secret_key, encoded_invalid_claims_jwt_token):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        with pytest.raises(TokenErrorException, match="The token claim is invalid."):
            jwt_utilities.decode_jwt_token(encoded_invalid_claims_jwt_token, secret_key)


def test_decode_jwt_expired_token(secret_key, encoded_expired_jwt_token):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        with pytest.raises(
            TokenErrorException, match="The token signature has expired."
        ):
            jwt_utilities.decode_jwt_token(encoded_expired_jwt_token, secret_key)


def test_decode_jwt_invalid_token(secret_key, encoded_invalid_jwt_token):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        with pytest.raises(
            TokenErrorException, match="The token signature is invalid."
        ) as e:
            jwt_utilities.decode_jwt_token(encoded_invalid_jwt_token, secret_key)
