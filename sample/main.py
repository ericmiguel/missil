"""Missil sample usage."""

import missil

from fastapi import FastAPI
from fastapi import Response

from typing import Union
from datetime import datetime
from datetime import timezone
from datetime import timedelta

app = FastAPI()

TOKEN_KEY = "Authorization"

# openssl rand -hex 32
SECRET_KEY = "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"

bearer = missil.FlexibleTokenBearer(TOKEN_KEY, SECRET_KEY, "userPermissions")
rules = missil.make_rules(bearer, "finances", "it", "other")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/set-cookies", status_code=200)
def set_cookies(response: Response) -> str:
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

    return "The token is stored as a cookie."


@app.get("/items/{item_id}", dependencies=[rules["finances:read"]])
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sample.main:app", port=8666, log_level="info", reload=True, reload_delay=0.5
    )
