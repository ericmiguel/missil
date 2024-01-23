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
def test_read_access(test_app, bearer_token):
    response = test_app.get("/finances/read", headers={"Authorization": bearer_token})

    assert response.status_code == 200
    assert response.json() == {
        "msg": "you have permission to perform read actions on finances!"
    }


@ignore_warnings
def test_write_access(test_app, bearer_token):
    response = test_app.get("/finances/write", headers={"Authorization": bearer_token})

    assert response.status_code == 403
    assert response.json() == {
        "detail": "insufficient access level: (0/1) on finances."
    }
