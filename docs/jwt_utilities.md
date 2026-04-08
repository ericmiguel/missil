# JWT Utilities

Missil uses [python-jose](https://github.com/mpdavis/python-jose) as backend to
offer JWT conveniences. These utilities are thin wrappers — you can use any JWT
library you prefer for token issuance as long as the payload structure matches
what your bearer expects.

## Encode JWT Token

Creates a signed JWT token from a claims dict.

### Usage Example

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
print(token)
```

### API Reference

::: missil.encode_jwt_token

---

## Decode JWT Token

Decodes and verifies a signed JWT token.

### Usage Example

```python
import missil

SECRET_KEY = "averysecretkey"

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = missil.decode_jwt_token(token, SECRET_KEY)

print(decoded)
# {"sub": "user123", "permissions": {"finances": 0, "it": 2}, "exp": ...}
```

!!! note
    `decode_jwt_token` raises `TokenValidationException` if the token is
    expired, has an invalid signature, or cannot be decoded.

### API Reference

::: missil.decode_jwt_token
