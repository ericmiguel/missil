import pytest

from starlette.testclient import TestClient

from sample.main import app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="function")
def bearer_token(test_app):
    test_app.get("/set-cookies")
    bearer_token = dict(test_app.cookies)["Authorization"].replace(" ", "")
    yield bearer_token
