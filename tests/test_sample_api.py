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
            "you have permission to perform write actions on finances!",
        ),
        ("/finances/write/router", "finances write rights check via qualified router!"),
    ],
)
def test_write_access(api_url, response_msg, test_app, bearer_token):
    response = test_app.get(api_url, headers={"Authorization": bearer_token})

    assert response.status_code == 200
    assert response.json() == {"msg": response_msg}


@ignore_warnings
@pytest.mark.parametrize(
    "api_url, response_msg",
    [
        ("/finances/admin", "you have admin permission on finances!"),
        ("/finances/admin/router", "finances admin rights check via qualified router!"),
    ],
)
def test_admin_access(api_url, response_msg, test_app, bearer_token):
    response = test_app.get(api_url, headers={"Authorization": bearer_token})

    assert response.status_code == 200
    assert response.json() == {"msg": response_msg}


@ignore_warnings
@pytest.mark.parametrize(
    "api_url",
    [
        "/user-profile",
    ],
)
def test_get_current_user(api_url, test_app, bearer_token, decoded_token):
    response = test_app.get(api_url, headers={"Authorization": bearer_token})
    assert response.status_code == 200
    assert response.json() == decoded_token


@ignore_warnings
def test_role_access(test_app, bearer_token):
    """Analyst Role (finances.READ + it.READ) passes with ADMIN/WRITE token."""
    response = test_app.get(
        "/analyst-dashboard",
        headers={"Authorization": bearer_token},
    )
    assert response.status_code == 200
    assert response.json() == {"msg": "analyst access granted!"}
