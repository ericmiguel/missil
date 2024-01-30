from missil import make_rule
from missil.rules import Area
from missil.rules import Rule


def test_make_rule(bearer_token):
    test_area = make_rule(bearer_token, "test")
    assert test_area.name == "test"
    assert isinstance(test_area, Area)
    assert isinstance(test_area.READ, Rule)
    assert isinstance(test_area.WRITE, Rule)
