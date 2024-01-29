<p align="center">
  <a href="https://ericmiguel.github.io/missil"><img src="https://github.com/ericmiguel/missil/assets/12076399/c7841626-706e-425f-99d6-c91fd6fb3455" alt="Missil"></a>
</p>
<p align="center">
    <em>Simple <a href="https://fastapi.tiangolo.com/">FastAPI</a> declarative endpoint-level access control, somewhat inspired by <a href="https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/security.html">Pyramid</a>.</em>
</p>
<p align="center">
    <span><a href="https://ericmiguel.github.io/missil/" target="_blank">[DOCS]</a></span>
    <span><a href="https://github.com/ericmiguel/missil" target="_blank">[SOURCE]</a></span>
</p>
<p align="center">
<a href="https://pypi.org/project/missil" target="_blank">
    <img src="https://img.shields.io/pypi/v/missil?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/missil" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/missil.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>


```python
@app.get("/", dependencies=[rules["finances"].READ])
def read_root():
    return {"Hello": "World"}
```

## Installation

```bash
pip install missil

```

## Why use Missil?

For most applications the use of [scopes]("https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/?h=oauth2") to determine the rights of a user is sufficient enough. Nonetheless, scopes are tied to the state of the user, while 'missil' also take the state of the requested resource into account.

Let's take an scientific paper as an example: depending on the state of the submission process (like "draft", "submitted", "peer review" or "published") different users should have different permissions on viewing and editing. This could be acomplished with custom code in the path definition functions, but Missil offers a very legible and to-the-point to define these constraints.

## Quick usage

```python

import missil

from fastapi import FastAPI
from fastapi import Response

app = FastAPI()

TOKEN_KEY = "Authorization"
SECRET_KEY = "2ef9451be5d149ceaf5be306b5aa03b41a0331218926e12329c5eeba60ed5cf0"

bearer = missil.FlexibleTokenBearer(TOKEN_KEY, SECRET_KEY)
rules = missil.make_rules(bearer, "finances", "it", "other")

@app.get("/", dependencies=[rules["finances"].READ])
def read_root():
    return {"Hello": "World"}


@app.get("/set-cookies")
def set_cookies(response: Response) -> None:
    """Just for example purposes."""
    sample_user_privileges = {
        "finances": missil.READ,
        "it": missil.WRITE,
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
```

## Disclaimer

Scopes did not meet my needs and other permission systems were too complex, so
I designed this code for me and my team needs, but feel free to use it if you like.

## License

This project is licensed under the terms of the MIT license.
