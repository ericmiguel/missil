<p align="center">
  <a href="https://ericmiguel.github.io/missil"><img src="https://github.com/ericmiguel/missil/assets/12076399/dfe4a649-a226-42b4-851d-698fbb664bc7" alt="Missil"></a>
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

---

## Installation

**Requirements:** Python 3.10+ · FastAPI 0.104.1+ · PyJWT 2.12.1+

```bash
pip install missil
```

## Why use Missil?

Permission checks tend to look the same across every protected endpoint: extract the token, verify it, find the area, check the level. Missil moves all of that out of your route functions and into a single declarative line per endpoint — keeping your business logic clean and your access rules explicit and auditable at a glance.

Because permissions are stored as numeric levels per business area, a single token can express fine-grained access across multiple areas of your application without requiring separate tokens or custom middleware.

## Quick example

```python
import missil
from fastapi import FastAPI, Response

app = FastAPI()
SECRET_KEY = "..."

# 1. Declare a bearer — reads token from cookie or Authorization header
bearer = missil.TokenBearer("Authorization", SECRET_KEY, permissions_key="permissions")

# 2. Declare business areas as typed attributes
class AppAreas(missil.AreasBase):
    finances: missil.Area
    it: missil.Area

areas = AppAreas(bearer)

# 3. Protect endpoints — one dependency, no boilerplate
@app.get("/finances/report", dependencies=[areas.finances.READ])
def finances_report(): ...

@app.get("/finances/edit", dependencies=[areas.finances.WRITE])
def finances_edit(): ...

@app.get("/it/admin", dependencies=[areas.it.ADMIN])
def it_admin(): ...

# 4. Issue a token at login
@app.post("/login")
def login(response: Response):
    claims = {
        "sub": "user123",
        "permissions": {"finances": missil.WRITE, "it": missil.READ},
    }
    token = missil.encode_jwt_token(claims, SECRET_KEY, expiration_hours=8)
    response.set_cookie("Authorization", f"Bearer {token}", httponly=True)
    return {"msg": "logged in"}
```

## Permission hierarchy

| Level | Constant | Satisfies |
|---|---|---|
| 0 | `READ` | READ |
| 1 | `WRITE` | READ, WRITE |
| 2 | `ADMIN` | READ, WRITE, ADMIN |

Higher levels automatically satisfy lower requirements — a user with `ADMIN` access can reach `READ` and `WRITE` protected endpoints without extra entries.

## Bearers

Choose the bearer that matches how your client sends the token:

| Bearer | Token source |
|---|---|
| `TokenBearer` | Cookie → falls back to `Authorization` header |
| `CookieTokenBearer` | Cookie only |
| `HeaderTokenBearer` | `Authorization` header only |

## License

This project is licensed under the terms of the MIT license.
