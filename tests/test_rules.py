from missil import make_rule
from missil import make_rules
from missil.rules import Area
from missil.rules import Rule


def test_make_rule(bearer_token):
    test_area = make_rule(bearer_token, "test")
    assert test_area.name == "test"
    assert isinstance(test_area, Area)
    assert isinstance(test_area.READ, Rule)
    assert isinstance(test_area.WRITE, Rule)


def test_make_rules_single_ba(bearer_token):
    test_area = make_rules(bearer_token, "test_1")
    assert "test_1" in test_area
    assert isinstance(test_area["test_1"], Area)
    assert isinstance(test_area["test_1"].READ, Rule)
    assert isinstance(test_area["test_1"].WRITE, Rule)


def test_make_rules_multiple_bas(bearer_token):
    test_areas = make_rules(bearer_token, "test_1", "test_2")
    assert "test_1" in test_areas
    assert "test_2" in test_areas
    assert isinstance(test_areas["test_1"], Area)
    assert isinstance(test_areas["test_2"], Area)
    assert isinstance(test_areas["test_1"].READ, Rule)
    assert isinstance(test_areas["test_2"].READ, Rule)
    assert isinstance(test_areas["test_1"].WRITE, Rule)
    assert isinstance(test_areas["test_2"].WRITE, Rule)
