# Access Rules

Missil core access control classes and permission level constants.

## Permission levels

| Constant | Value | Satisfies |
|---|---|---|
| `READ` | 0 | READ |
| `WRITE` | 1 | READ, WRITE |
| `ADMIN` | 2 | READ, WRITE, ADMIN |

## AreasBase

The recommended way to declare business areas. Subclass `AreasBase` and annotate
each area as a `missil.Area` field. On instantiation, all `Area` objects are
created automatically and accessible as typed attributes.

```python
import missil

jwt_bearer = missil.TokenBearer("Authorization", SECRET_KEY, "userPermissions")


class AppAreas(missil.AreasBase):
    finances: missil.Area
    it: missil.Area
    hr: missil.Area


areas = AppAreas(jwt_bearer)


@app.get("/report", dependencies=[areas.finances.READ])
def report(): ...


@app.get("/admin", dependencies=[areas.finances.ADMIN])
def admin(): ...
```

Annotations typed as anything other than `missil.Area` are silently ignored,
so you can freely add non-area class attributes to your subclass.

::: missil.AreasBase

## Area

::: missil.Area

## AccessRule

::: missil.AccessRule

---

## Migrating from make_areas / make_area

!!! danger "Deprecated — will be removed in a future version"
    `make_areas()` and `make_area()` are deprecated. Use [`AreasBase`](#areasbase)
    or [`Area`](#area) directly instead. See the migration guide below.

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

## make_area

!!! danger "Deprecated"
    Use `missil.Area(name, bearer)` directly instead.

::: missil.make_area

## make_areas

!!! danger "Deprecated"
    Use [`AreasBase`](#areasbase) instead. See the migration guide above.

::: missil.make_areas
