<p align="center">
  <a href="https://ericmiguel.github.io/missil"><img src="assets/logo/logo_small.png" alt="Missil"></a>
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

**Requirements:** Python 3.10+ · FastAPI 0.135.3+ · PyJWT 2.12.1+

<!-- termynal -->

```
> pip install missil
---> 100%
Installed
```

## Why use Missil?

Permission checks tend to look the same across every protected endpoint: extract the [token](guide/jwt.md), verify it, find the area, check the level. Missil moves all of that out of your route functions and into a single declarative line per endpoint — keeping your business logic clean and your access rules explicit and auditable at a glance.

It also goes beyond simple scope checks: because permissions are stored as [numeric levels](guide/access-control.md#permission-levels) per business area, a single token can express fine-grained access across multiple areas of your application without requiring separate tokens or custom middleware.

## End-to-end example

```python
import missil
from fastapi import FastAPI, Response

app = FastAPI()
SECRET_KEY = "..."

# 1. Declare a bearer — reads token from cookie or Authorization header (see Bearers guide)
bearer = missil.TokenBearer("Authorization", SECRET_KEY, permissions_key="permissions")

# 2. Declare business areas as typed attributes (see Access Control guide)
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

# 4. Issue the token (e.g. at login)
@app.post("/login")
def login(response: Response):
    claims = {"sub": "user123", "permissions": {"finances": missil.WRITE, "it": missil.READ}}
    token = missil.encode_jwt_token(claims, SECRET_KEY, expiration_hours=8)
    response.set_cookie("Authorization", f"Bearer {token}", httponly=True)
    return {"msg": "logged in"}
```

## How it works

Missil works in three steps:

**1. Issue a [JWT token](guide/jwt.md)** containing a permissions dict under a key of your choice:

```python
claims = {
    "sub": "user123",
    "permissions": {       # key name must match the bearer's permissions_key
        "finances": 0,     # READ
        "it": 2,           # ADMIN
    },
}
token = missil.encode_jwt_token(claims, SECRET_KEY, expiration_hours=8)
```

**2. Declare a [bearer](guide/bearers.md)** that knows where to find the token and which key holds permissions:

```python
bearer = missil.TokenBearer("Authorization", SECRET_KEY, permissions_key="permissions")
```

**3. [Declare areas](guide/access-control.md#declaring-areas-with-areasbase) and protect endpoints:**

```python
class AppAreas(missil.AreasBase):
    finances: missil.Area
    it: missil.Area

areas = AppAreas(bearer)

@app.get("/report", dependencies=[areas.finances.READ])   # level 0+
def report(): ...

@app.get("/dashboard", dependencies=[areas.it.ADMIN])     # level 2 only
def dashboard(): ...
```

On every request, Missil extracts the token, decodes it, looks up the area in the
permissions dict and checks that the user's level satisfies the required level.
If not, it raises [`PermissionDeniedException`](guide/exceptions.md) (HTTP 403).

### JWT payload structure

Missil expects the JWT payload to include a dict under the key you passed as
`permissions_key` to the [bearer](guide/bearers.md#choosing-a-bearer). Each entry maps an area name to a numeric access level:

```json
{
  "sub": "user123",
  "exp": 1234567890,
  "permissions": {
    "finances": 0,
    "it": 2,
    "hr": 1
  }
}
```

!!! warning "Key name must match"
    The key name in the JWT payload (`"permissions"` above) must exactly match
    the `permissions_key` argument passed to your [bearer constructor](guide/bearers.md#choosing-a-bearer).

### Permission Hierarchy

| Level | Constant | Satisfies |
|---|---|---|
| 0 | `READ` | READ |
| 1 | `WRITE` | READ, WRITE |
| 2 | `ADMIN` | READ, WRITE, ADMIN |

Higher permission levels automatically satisfy lower requirements — a user with
`ADMIN` access can reach `READ` and `WRITE` protected endpoints without needing
separate permission entries. See the [Access Control guide](guide/access-control.md#permission-levels) for details.

### Grouping rules with Role

When multiple areas must be verified together, use `Role` to define the combination
once and reuse it across endpoints:

```python
analyst = missil.Role(areas.finances.READ, areas.it.READ)

@app.get("/dashboard", dependencies=[analyst])
def dashboard(): ...
```

See the [Access Control guide](guide/access-control.md#grouping-rules-with-role) for full details.

## Sending the token

Depending on which [bearer](guide/bearers.md#choosing-a-bearer) you chose, the client sends the token differently:

=== "Cookie (TokenBearer / CookieTokenBearer)"

    Issue the token as a cookie at login — the bearer reads it automatically on every subsequent request:

    ```python
    @app.post("/login")
    def login(response: Response):
        token = missil.encode_jwt_token(claims, SECRET_KEY, expiration_hours=8)
        response.set_cookie(
            key="Authorization",   # must match the bearer's token_key
            value=f"Bearer {token}",
            httponly=True,
        )
        return {"msg": "logged in"}
    ```

    The client needs no extra code — the browser sends the cookie automatically.

=== "Header (TokenBearer / HeaderTokenBearer)"

    ```http
    GET /finances/report HTTP/1.1
    Authorization: Bearer <your-token>
    ```

    ```python
    import httpx
    response = httpx.get("http://localhost:8000/finances/report",
                         headers={"Authorization": f"Bearer {token}"})
    ```

## License

This project is licensed under the terms of the MIT license.