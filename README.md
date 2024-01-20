# Missil

Simple FastAPI declarative endpoint-level access control.

Scopes did not meet my needs and other permission systems were too complex, so
I designed this code for my and my team needs, but feel free to use it if you like.

A very humble example:

```python
import missil

from fastapi import FastAPI
from fastapi import Response

from typing import Union
from datetime import datetime
from datetime import timezone
from datetime import timedelta

app = FastAPI()

TOKEN_KEY = "Authorization"
SECRET_KEY = "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"

bearer = missil.FlexibleTokenBearer(TOKEN_KEY, SECRET_KEY)
rules = missil.make_rules(bearer, "finances", "it", "other")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/set-cookies")
def set_cookies(response: Response) -> None:
    """Just for example purposes."""
    sample_user_privileges = {
        "finances": missil.READ,
        "it": missil.WRITE,
    }

    token_expiration = datetime.now(timezone.utc) + timedelta(hours=8)
    token = missil.make_jwt_token(sample_user_privileges, SECRET_KEY, token_expiration)

    response.set_cookie(
        key=TOKEN_KEY,
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )


@app.get("/items/{item_id}", dependencies=[rules["finances:read"]])
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```
