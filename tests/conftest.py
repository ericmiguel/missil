import json

import pytest
from starlette.testclient import TestClient

from missil import decode_jwt_token
from sample.main import app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def bearer_token(test_app):
    test_app.get("/set-cookies")
    bearer_token = json.loads(test_app.cookies["Authorization"]).replace("Bearer ", "")
    print(f"Bearer token: {bearer_token}")
    yield bearer_token


@pytest.fixture(scope="module")
def jwt_secret_key():
    return "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"


@pytest.fixture(scope="module")
def decoded_token(bearer_token, jwt_secret_key):
    return decode_jwt_token(bearer_token, jwt_secret_key)
