# Access Control

## Permission levels

Missil uses a three-level hierarchy. Higher levels satisfy all lower requirements —
a user with `ADMIN` access can reach `READ` and `WRITE` protected endpoints without
needing separate permission entries.

| Constant | Value | Satisfies |
|---|---|---|
| `READ` | 0 | READ |
| `WRITE` | 1 | READ, WRITE |
| `ADMIN` | 2 | READ, WRITE, ADMIN |

## Declaring areas with AreasBase

`AreasBase` is the recommended way to declare business areas. Subclass it and
annotate each area as a `missil.Area` field. On instantiation, all `Area` objects
are created automatically and accessible as typed attributes.

```python
import missil

# See the Bearers guide for bearer options
bearer = missil.TokenBearer("Authorization", SECRET_KEY, permissions_key="permissions")


class AppAreas(missil.AreasBase):
    finances: missil.Area
    it: missil.Area
    hr: missil.Area


areas = AppAreas(bearer)
```

Each area exposes `READ`, `WRITE`, and `ADMIN` attributes, each of which is a
ready-to-use FastAPI `Depends`:

```python
@app.get("/report", dependencies=[areas.finances.READ])
def report(): ...

@app.get("/edit", dependencies=[areas.finances.WRITE])
def edit(): ...

@app.get("/admin", dependencies=[areas.finances.ADMIN])
def admin(): ...
```

Annotations typed as anything other than `missil.Area` are silently ignored,
so you can freely mix area fields with other class attributes.

## Grouping rules with Role

Use `Role` to bundle multiple `AccessRule` objects into a single FastAPI `Depends`.
The endpoint is accessible only when **every rule** passes — if any fails, FastAPI
returns HTTP 403.

Define the role once and reuse it across as many endpoints as needed:

```python
analyst = missil.Role(areas.finances.READ, areas.it.READ)

@app.get("/dashboard", dependencies=[analyst])
def dashboard(): ...

@app.get("/report", dependencies=[analyst])
def report(): ...
```

A `Role` is a standard FastAPI `Depends` and can be combined with other
dependencies on the same endpoint:

```python
@app.get("/report", dependencies=[analyst, Depends(rate_limiter)])
def report(): ...
```

---

**See also:**

- [Bearers guide](bearers.md) — how to create and configure a bearer
- [JWT guide](jwt.md) — payload structure and token issuance
- [API Reference → Rules](../reference/rules.md) — `AreasBase`, `Area`, `AccessRule`, `Role`
