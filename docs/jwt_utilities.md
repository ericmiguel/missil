# JWT Utitilies

Missil uses the excellent [Python-jose](https://github.com/mpdavis/python-jose) as backend to offer some JWT conveniences.


## Encode JWT Token

### Usage Example

```python
from datetime import datetime
from missil import encode_jwt_token

SECRET_KEY = "averysecretkey"

base_date = datetime(2094, 2, 26)
claims = {"name": "John Doe", "userPrivileges": {"finances": 1}}
token = encode_jwt_token(claims, SECRET_KEY, 8, base=base_date)

print(token)
```

### API Reference

#### ::: missil.encode_jwt_token

---


## Decode JWT Token

### Usage Example

```python
from missil import decode_jwt_token

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiSm9obiBEb2UiLCJ1c2VyUHJpdmlsZWdlcyI6eyJmaW5hbmNlcyI6MX0sImV4cCI6MzkxODY3MjAwMH0.BWkskBJZj68mLaxqgdO0occL_FY8RSdEnqNSC6Swxh0"
SECRET_KEY = "averysecretkey"
decoded_token = decode_jwt_token(TOKEN, SECRET_KEY)

print(decoded_token)  # {'name': 'John Doe', 'userPrivileges': {'finances': 1}, 'exp': 3918672000}

```

### API Reference

#### ::: missil.decode_jwt_token