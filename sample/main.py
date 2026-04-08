"""Missil sample usage."""

from typing import Annotated

from fastapi import FastAPI
from fastapi import Response

import missil
from missil import JWTClaims
from missil.routers import ProtectedRouter


class SampleClaims(JWTClaims, total=False):
    """Application-specific JWT claims for this sample app."""

    username: str
    userPermissions: dict[str, int]


app = FastAPI()

TOKEN_KEY = "Authorization"

# openssl rand -hex 32
SECRET_KEY = "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"

bearer = missil.TokenBearer(TOKEN_KEY, SECRET_KEY, "userPermissions")


class AppAreas(missil.AreasBase):
    """Application business areas."""

    """Application business areas."""

    finances: missil.Area
    it: missil.Area
    other: missil.Area


areas = AppAreas(bearer)

analyst = missil.Role(areas.finances.READ, areas.it.READ)

finances_read_router = ProtectedRouter(rules=[areas.finances.READ])
finances_write_router = ProtectedRouter(rules=[areas.finances.WRITE])
finances_admin_router = ProtectedRouter(rules=[areas.finances.ADMIN])


@app.get("/")
def read_root() -> dict[str, str]:
    """Just a humble and happy endpoint."""
    return {"Hello": "World"}


@app.get("/set-cookies", status_code=200)
def set_cookies(response: Response) -> dict[str, str]:
    """Just for example purposes."""
    claims: SampleClaims = {
        "username": "JohnDoe",
        # the key 'userPermissions' name must match the TokenBearer instance
        "userPermissions": {
            "finances": missil.ADMIN,
            "it": missil.WRITE,
        },
    }

    token_expiration_in_hours = 8
    token = missil.encode_jwt_token(claims, SECRET_KEY, token_expiration_in_hours)

    response.set_cookie(
        key=TOKEN_KEY,
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )

    return {"msg": "The Authorization token is stored as a cookie."}


@app.get("/finances/read", dependencies=[areas.finances.READ])
def finances_read() -> dict[str, str]:
    """Require read permission on finances."""
    return {"msg": "you have permission to perform read actions on finances!"}


@app.get("/finances/write", dependencies=[areas.finances.WRITE])
def finances_write() -> dict[str, str]:
    """Require write permission on finances."""
    return {"msg": "you have permission to perform write actions on finances!"}


@app.get("/finances/admin", dependencies=[areas.finances.ADMIN])
def finances_admin() -> dict[str, str]:
    """Require admin permission on finances."""
    return {"msg": "you have admin permission on finances!"}


@app.get("/analyst-dashboard", dependencies=[analyst])
def analyst_dashboard() -> dict[str, str]:
    """Require finances READ and it READ via Role."""
    return {"msg": "analyst access granted!"}


@app.get("/user-profile", dependencies=[areas.it.READ])
def get_user_profile(
    user_profile: Annotated[SampleClaims, areas.it.READ],
) -> SampleClaims:
    """Require read permission on it."""
    return user_profile


@finances_read_router.get("/finances/read/router")
def finances_read_route() -> dict[str, str]:
    """Require read permission on finances."""
    return {"msg": "finances read rights check via qualified router!"}


@finances_write_router.get("/finances/write/router")
def finances_write_route() -> dict[str, str]:
    """Require write permission on finances."""
    return {"msg": "finances write rights check via qualified router!"}


@finances_admin_router.get("/finances/admin/router")
def finances_admin_route() -> dict[str, str]:
    """Require admin permission on finances."""
    return {"msg": "finances admin rights check via qualified router!"}


app.include_router(finances_read_router)
app.include_router(finances_write_router)
app.include_router(finances_admin_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sample.main:app", port=8666, log_level="info", reload=True, reload_delay=0.5
    )
