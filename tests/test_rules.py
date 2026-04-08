from missil import make_scope
from missil import make_scopes
from missil.rules import AccessRule
from missil.rules import Scope


def test_make_scope(bearer_token):
    test_scope = make_scope(bearer_token, "test")
    assert test_scope.name == "test"
    assert isinstance(test_scope, Scope)
    assert isinstance(test_scope.READ, AccessRule)
    assert isinstance(test_scope.WRITE, AccessRule)


def test_make_scopes_single(bearer_token):
    test_scopes = make_scopes(bearer_token, "test_1")
    assert "test_1" in test_scopes
    assert isinstance(test_scopes["test_1"], Scope)
    assert isinstance(test_scopes["test_1"].READ, AccessRule)
    assert isinstance(test_scopes["test_1"].WRITE, AccessRule)


def test_make_scopes_multiple(bearer_token):
    test_scopes = make_scopes(bearer_token, "test_1", "test_2")
    assert "test_1" in test_scopes
    assert "test_2" in test_scopes
    assert isinstance(test_scopes["test_1"], Scope)
    assert isinstance(test_scopes["test_2"], Scope)
    assert isinstance(test_scopes["test_1"].READ, AccessRule)
    assert isinstance(test_scopes["test_2"].READ, AccessRule)
    assert isinstance(test_scopes["test_1"].WRITE, AccessRule)
    assert isinstance(test_scopes["test_2"].WRITE, AccessRule)
