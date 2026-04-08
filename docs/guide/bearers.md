# Bearers

A bearer is a FastAPI dependency responsible for extracting and decoding the JWT
token on every request. Choose the bearer that matches how your client sends the token.

## Choosing a bearer

| Bearer | Token source | Recommended when |
|---|---|---|
| `TokenBearer` | Cookie → falls back to `Authorization` header | Most apps: supports both browser (cookie) and API (header) clients |
| `CookieTokenBearer` | Cookie only | Browser-only apps with cookie-based auth |
| `HeaderTokenBearer` | `Authorization` header only | Pure API / mobile clients |

All bearers share the same constructor signature:

```python
bearer = missil.TokenBearer(
    token_key="Authorization",   # cookie name or header name
    secret_key="...",            # JWT signing secret
    permissions_key="perms",     # key in JWT payload holding the permissions dict
    algorithms="HS256",          # optional, defaults to HS256
)
```

!!! tip "Use the same `permissions_key` everywhere"
    The value of `permissions_key` must exactly match the key used when issuing
    the token. If you sign tokens with `{"perms": {"finances": 1}}` but declare
    the bearer with `permissions_key="permissions"`, every request will fail.
    See the [JWT guide](jwt.md#payload-structure) for the full payload structure.

## Token revocation

By default, all tokens that pass signature and expiry validation are accepted.
To implement a revocation strategy (e.g. a Redis blocklist, a database table of
invalidated JTIs), subclass any bearer and override `is_revoked`:

```python
import missil
from missil.types import JWTClaims

revoked_jtis: set[str] = set()  # replace with your store


class RevokableBearer(missil.TokenBearer):
    def is_revoked(self, decoded_token: JWTClaims) -> bool:
        jti = decoded_token.get("jti")
        return jti in revoked_jtis


jwt_bearer = RevokableBearer("Authorization", SECRET_KEY, "permissions")
```

When `is_revoked` returns `True`, the bearer raises [`TokenValidationException`](exceptions.md)
with HTTP 403 before the permission check ever runs.

!!! note
    `is_revoked` receives the **decoded** claims dict, so you have access to any
    field in the payload (`jti`, `sub`, `iat`, etc.) to make the revocation
    decision.

## Working with JWT claims

Every bearer returns the decoded JWT payload as a `JWTClaims` dict. You can
access it in endpoint parameters by annotating with the claims type:

```python
from typing import Annotated
import missil
from missil import JWTClaims


# Optional: subclass JWTClaims to add app-specific fields
class AppClaims(JWTClaims, total=False):
    username: str
    permissions: dict[str, int]  # must match permissions_key


jwt_bearer = missil.TokenBearer("Authorization", SECRET_KEY, "permissions")


class AppAreas(missil.AreasBase):
    finances: missil.Area


areas = AppAreas(jwt_bearer)


@app.get("/profile", dependencies=[areas.finances.READ])
def profile(user: Annotated[AppClaims, areas.finances.READ]) -> AppClaims:
    username = user["username"]  # typed as str
    return user
```

`JWTClaims` is a `TypedDict` covering all standard RFC 7519 registered claims
(`exp`, `iat`, `nbf`, `sub`, `iss`, `aud`, `jti`). Subclassing it adds your
app-specific fields while keeping the object a plain `dict` at runtime —
no serialization overhead.

---

**See also:**

- [Access Control guide](access-control.md) — declaring areas and protecting endpoints
- [Exceptions guide](exceptions.md) — handling `TokenValidationException` and `PermissionDeniedException`
- [API Reference → Bearers](../reference/bearers.md) — `TokenBearer`, `CookieTokenBearer`, `HeaderTokenBearer`, `JWTClaims`
