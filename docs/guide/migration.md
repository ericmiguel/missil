# Migration Guide

## make_areas / make_area → AreasBase / Area

!!! danger "Deprecated — will be removed in a future version"
    `make_areas()` and `make_area()` are deprecated. Use [`AreasBase`](access-control.md#declaring-areas-with-areasbase)
    or `missil.Area` directly instead.

=== "Before (make_areas)"

    ```python
    areas = missil.make_areas(bearer, "finances", "it", "hr")

    @app.get("/report", dependencies=[areas["finances"].READ])
    def report(): ...
    ```

=== "After (AreasBase)"

    ```python
    class AppAreas(missil.AreasBase):
        finances: missil.Area
        it: missil.Area
        hr: missil.Area

    areas = AppAreas(bearer)

    @app.get("/report", dependencies=[areas.finances.READ])
    def report(): ...
    ```

=== "Before (make_area)"

    ```python
    finances = missil.make_area(bearer, "finances")
    ```

=== "After (Area directly)"

    ```python
    finances = missil.Area("finances", bearer)
    ```

---

**See also:**

- [Access Control guide](access-control.md) — full `AreasBase` usage guide
- [API Reference → Rules](../reference/rules.md#make_area) — deprecated signatures
