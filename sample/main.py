"""Missil sample usage."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import FastAPI
from fastapi import Response

import missil


app = FastAPI()

TOKEN_KEY = "Authorization"

# openssl rand -hex 32
SECRET_KEY = "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"

bearer = missil.FlexibleTokenBearer(TOKEN_KEY, SECRET_KEY, "userPermissions")
rules = missil.make_rules(bearer, "finances", "it", "other")


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

    token_expiration = datetime.now(timezone.utc) + timedelta(hours=8)
    token = missil.encode_jwt_token(claims, SECRET_KEY, token_expiration)

    response.set_cookie(
        key=TOKEN_KEY,
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )

    return {"msg": "The Authorization token is stored as a cookie."}


@app.get("/finances/read", dependencies=[rules["finances:read"]])
def finances_read() -> dict[str, str]:
    """Requires read permission on finances."""
    return {"msg": "you have permission to perform read actions on finances!"}


@app.get("/finances/write", dependencies=[rules["finances:write"]])
def finances_write() -> dict[str, str]:
    """Requires write permission on finances."""
    return {"msg": "you have permission to perform write actions on finances!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sample.main:app", port=8666, log_level="info", reload=True, reload_delay=0.5
    )
