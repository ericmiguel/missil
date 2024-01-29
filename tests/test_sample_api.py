import pytest

from tests.utils import ignore_warnings


def test_set_bearer_token_cookies(test_app):
    response = test_app.get("/set-cookies")
    assert response.status_code == 200
    assert "Authorization" in dict(test_app.cookies)


def test_ping(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@ignore_warnings
@pytest.mark.parametrize(
    "api_url, response_msg",
    [
        ("/finances/read", "you have permission to perform read actions on finances!"),
        ("/finances/read/router", "finances read rights check via qualified router!"),
    ],
)
def test_read_access(api_url, response_msg, test_app, bearer_token):
    response = test_app.get(api_url, headers={"Authorization": bearer_token})

    assert response.status_code == 200
    assert response.json() == {"msg": response_msg}


@ignore_warnings
@pytest.mark.parametrize(
    "api_url, response_msg",
    [
        (
            "/finances/write",
            "insufficient access level: (0/1) on finances.",
        ),
        ("/finances/write/router", "insufficient access level: (0/1) on finances."),
    ],
)
def test_write_access(api_url, response_msg, test_app, bearer_token):
    response = test_app.get(api_url, headers={"Authorization": bearer_token})

    assert response.status_code == 403
    assert response.json() == {"detail": response_msg}
