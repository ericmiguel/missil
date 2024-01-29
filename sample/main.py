"""Missil sample usage."""

from fastapi import FastAPI
from fastapi import Response

import missil

from missil.routers import QualifiedRouter


app = FastAPI()

TOKEN_KEY = "Authorization"

# openssl rand -hex 32
SECRET_KEY = "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"

bearer = missil.FlexibleTokenBearer(TOKEN_KEY, SECRET_KEY, "userPermissions")
bas = missil.make_rules(bearer, "finances", "it", "other")  # business areas

finances_read_router = QualifiedRouter(rules=[bas["finances"].READ])
finances_write_router = QualifiedRouter(rules=[bas["finances"].WRITE])


@app.get("/")
def read_root() -> dict[str, str]:
    """Just a humble and happy endpoint."""
    return {"Hello": "World"}


@app.get("/set-cookies", status_code=200)
def set_cookies(response: Response) -> dict[str, str]:
    """Just for example purposes."""
    claims = {
        "username": "JohnDoe",
        # the key 'userPermissions' name must be the same as in the
        # FlexibleTokenBearer instance
        "userPermissions": {
            "finances": missil.READ,
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


@app.get("/finances/read", dependencies=[bas["finances"].READ])
def finances_read() -> dict[str, str]:
    """Requires read permission on finances."""
    return {"msg": "you have permission to perform read actions on finances!"}


@app.get("/finances/write", dependencies=[bas["finances"].WRITE])
def finances_write() -> dict[str, str]:
    """Requires write permission on finances."""
    return {"msg": "you have permission to perform write actions on finances!"}


@finances_read_router.get("/finances/read/router")
def finances_read_route() -> dict[str, str]:
    """Requires read permission on finances."""
    return {"msg": "finances read rights check via qualified router!"}


@finances_write_router.get("/finances/write/router")
def finances_write_route() -> dict[str, str]:
    """Requires read permission on finances."""
    return {"msg": "finances write rights check via qualified router!"}


app.include_router(finances_read_router)
app.include_router(finances_write_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sample.main:app", port=8666, log_level="info", reload=True, reload_delay=0.5
    )
