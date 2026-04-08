# Routers

## ProtectedRouter

`ProtectedRouter` is a FastAPI [APIRouter](https://fastapi.tiangolo.com/reference/apirouter/)
with a `rules` parameter. Use it to avoid repeating the same rule declaration on
every endpoint of the same business area. Rules passed to the router behave exactly
like the [`AccessRule`](../reference/rules.md#accessrule) objects produced by
[`Area`](access-control.md#declaring-areas-with-areasbase).

## Router-level vs endpoint-level rules

Understanding when each rule fires is important:

| Rule placement | Evaluated on |
|---|---|
| `ProtectedRouter(rules=[...])` | **Every** route registered on this router |
| `@router.get(..., dependencies=[...])` | Only that specific endpoint, **in addition** to router rules |

Endpoint-level rules stack on top of router rules — both must pass.

A common pattern is to set the minimum required level at the router (`READ`) and
use endpoint-level dependencies to raise the bar for specific routes (`WRITE`, `ADMIN`):

```python
import missil
from missil.routers import ProtectedRouter
from fastapi import FastAPI

app = FastAPI()

SECRET_KEY = "verysecuresecret"
jwt_bearer = missil.HeaderTokenBearer("Authorization", SECRET_KEY, "userPermissions")


class AppAreas(missil.AreasBase):
    finances: missil.Area


areas = AppAreas(jwt_bearer)

# All routes on this router require at least READ on finances
finances_router = ProtectedRouter(rules=[areas.finances.READ])


@finances_router.get("/finances/read")
async def finances_read_route() -> dict[str, str]:
    """READ is covered by the router rule — no extra dependency needed."""
    return {"msg": "finances read access granted"}


@finances_router.get("/finances/write", dependencies=[areas.finances.WRITE])
async def finances_write_route() -> dict[str, str]:
    """Router enforces READ; this endpoint additionally requires WRITE."""
    return {"msg": "finances write access granted"}


@finances_router.get("/finances/admin", dependencies=[areas.finances.ADMIN])
async def finances_admin_route() -> dict[str, str]:
    """Router enforces READ; this endpoint additionally requires ADMIN."""
    return {"msg": "finances admin access granted"}


app.include_router(finances_router)
```

---

**See also:**

- [Access Control guide](access-control.md) — `AreasBase`, permission levels, `Role`
- [Bearers guide](bearers.md) — bearer options and configuration
- [API Reference → Routers](../reference/routers.md) — `ProtectedRouter`
