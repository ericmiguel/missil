# JWT Utilities

Missil uses [PyJWT](https://pyjwt.readthedocs.io/) as JWT backend. These utilities
are thin wrappers — you can use any JWT library you prefer for token issuance as
long as the payload structure matches what your bearer expects.

## Payload structure

Missil expects the JWT payload to include a dict under the key you passed as
`permissions_key` to the bearer. Each entry maps a business area name to a
numeric access level:

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

The area names must exactly match the attribute names you declared in your
[`AreasBase`](access-control.md#declaring-areas-with-areasbase) subclass.
The numeric levels map to the permission constants:

| Value | Constant |
|---|---|
| `0` | `READ` |
| `1` | `WRITE` |
| `2` | `ADMIN` |

!!! warning "Key name must match"
    The key name in the payload (`"permissions"` above) must exactly match the
    `permissions_key` argument passed to your [bearer constructor](bearers.md#choosing-a-bearer).
    A mismatch means every request will fail with HTTP 403.

## Encoding tokens

Use `encode_jwt_token` to create a signed token from a claims dict. The
`permissions` dict under your chosen `permissions_key` is what Missil will read
on every protected request.

```python
import missil

SECRET_KEY = "averysecretkey"

claims = {
    "sub": "user123",
    "permissions": {       # key must match the bearer's permissions_key
        "finances": missil.READ,
        "it": missil.ADMIN,
    },
}

token = missil.encode_jwt_token(claims, SECRET_KEY, expiration_hours=8)
```

## Decoding tokens

Use `decode_jwt_token` to verify and decode a token. Missil's bearers call this
internally — you typically only need it directly in tests or for token inspection.

```python
import missil

SECRET_KEY = "averysecretkey"

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = missil.decode_jwt_token(token, SECRET_KEY)

print(decoded)
# {"sub": "user123", "permissions": {"finances": 0, "it": 2}, "exp": ...}
```

!!! note
    `decode_jwt_token` raises [`TokenValidationException`](exceptions.md) if the
    token is expired, has an invalid signature, or cannot be decoded.

---

**See also:**

- [Bearers guide](bearers.md) — how bearers use these utilities internally
- [API Reference → JWT](../reference/jwt.md) — `encode_jwt_token`, `decode_jwt_token`
