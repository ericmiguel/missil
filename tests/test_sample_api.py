from starlette.testclient import TestClient

from sample.main import app

client = TestClient(app)


def test_ping(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
