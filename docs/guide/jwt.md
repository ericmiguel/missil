# JWT Utilities

Missil uses [PyJWT](https://pyjwt.readthedocs.io/) as JWT backend. These utilities
are thin wrappers — you can use any JWT library you prefer for token issuance as
long as the payload structure matches what your bearer expects.

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
    `decode_jwt_token` raises `TokenValidationException` if the token is expired,
    has an invalid signature, or cannot be decoded.

---

See the [API Reference → JWT](../reference/jwt.md) for full function signatures.
