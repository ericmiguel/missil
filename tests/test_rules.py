import pytest

from missil import make_area
from missil import make_areas
from missil.rules import AccessRule
from missil.rules import Area
from missil.rules import AreasBase
from missil.rules import Role


class TestAreasBase:
    """Tests for AreasBase."""

    def test_areas_created_as_attributes(self, bearer_token):
        """Declared Area fields are instantiated as typed attributes."""

        class AppAreas(AreasBase):
            finances: Area
            it: Area

        areas = AppAreas(bearer_token)
        assert isinstance(areas.finances, Area)
        assert isinstance(areas.it, Area)

    def test_area_names_match_field_names(self, bearer_token):
        """Each Area's internal name matches its attribute name."""

        class AppAreas(AreasBase):
            finances: Area

        areas = AppAreas(bearer_token)
        assert areas.finances.name == "finances"

    def test_access_rules_created(self, bearer_token):
        """Area fields expose READ and WRITE AccessRule instances."""

        class AppAreas(AreasBase):
            finances: Area

        areas = AppAreas(bearer_token)
        assert isinstance(areas.finances.READ, AccessRule)
        assert isinstance(areas.finances.WRITE, AccessRule)

    def test_non_area_annotations_ignored(self, bearer_token):
        """Non-Area typed annotations are silently ignored."""

        class AppAreas(AreasBase):
            finances: Area
            label: str

        areas = AppAreas(bearer_token)
        assert isinstance(areas.finances, Area)
        assert not hasattr(areas, "label")


def test_make_scope(bearer_token):
    with pytest.warns(DeprecationWarning):
        test_scope = make_area(bearer_token, "test")
    assert test_scope.name == "test"
    assert isinstance(test_scope, Area)
    assert isinstance(test_scope.READ, AccessRule)
    assert isinstance(test_scope.WRITE, AccessRule)


def test_make_scopes_single(bearer_token):
    with pytest.warns(DeprecationWarning):
        test_scopes = make_areas(bearer_token, "test_1")
    assert "test_1" in test_scopes
    assert isinstance(test_scopes["test_1"], Area)
    assert isinstance(test_scopes["test_1"].READ, AccessRule)
    assert isinstance(test_scopes["test_1"].WRITE, AccessRule)


def test_make_scopes_multiple(bearer_token):
    with pytest.warns(DeprecationWarning):
        test_scopes = make_areas(bearer_token, "test_1", "test_2")
    assert "test_1" in test_scopes
    assert "test_2" in test_scopes
    assert isinstance(test_scopes["test_1"], Area)
    assert isinstance(test_scopes["test_2"], Area)
    assert isinstance(test_scopes["test_1"].READ, AccessRule)
    assert isinstance(test_scopes["test_2"].READ, AccessRule)
    assert isinstance(test_scopes["test_1"].WRITE, AccessRule)
    assert isinstance(test_scopes["test_2"].WRITE, AccessRule)


def test_role_creation(bearer_token):
    """Role wraps multiple AccessRules into a single dependency."""
    area = Area("finances", bearer_token)
    role = Role(area.READ, area.WRITE)
    assert len(role.rules) == 2


def test_role_is_fastapi_depends(bearer_token):
    """Role is a FastAPI Depends instance and can be used in dependencies=[]."""
    area = Area("finances", bearer_token)
    role = Role(area.READ)
    assert hasattr(role, "dependency")
    assert callable(role.dependency)
