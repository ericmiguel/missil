# Missil

Simple FastAPI declarative endpoint-level access control.

Scopes did not meet my needs and other permission systems were too complex, so
I designed this code for my and my team needs, but feel free to use it if you like.

A very humble example:

```python
from typing import Union
from missil import Permission
from missil import READ
from missil import WRITE
from fastapi import FastAPI
from fastapi import Response
import json

app = FastAPI()

permission = {
    "finances:read": Permission("finances", READ),
    "finances:write": Permission("finances", WRITE),
}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/set-cookies")
def set_cookies(response: Response) -> str:
    """Just for example purposes."""
    sample_user_privileges = {
        "finances": 0,  # you can  also use missil constant READ
        "tecnology": 1  # you can  also use missil constant WRITE
    }

    response.set_cookie(
        key="UserPermissions",
        value=json.dumps(sample_user_privileges),
        httponly=True,
        max_age=1800,
        expires=1800,
    )


@app.get("/items/{item_id}", dependencies=[permission["finances:write"]])
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```
