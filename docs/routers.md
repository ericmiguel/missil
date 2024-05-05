# Routers

## Qualified Router

FastAPI [APIrouter](https://fastapi.tiangolo.com/reference/apirouter/) with a 'rules' parameter.

Use it to avoid multiple and/or redudant rule declarations in same business area endpoints.

!!! tip "Lorem ipsum"

    You can also declare aditional rules in a `Qualified Router`, as it will also get evaluated in addition
    to the already declared router rules.
    
### Usage example

```python
# qualified_router.py

import missil
from missil.routers import QualifiedRouter
from fastapi import FastAPI

app = FastAPI()

TOKEN_KEY = "Authorization"
SECRET_KEY = "verysecuresecret"

# will expect a token sent in the Authorization header 
bearer = missil.HTTPTokenBearer(TOKEN_KEY, SECRET_KEY, "userPermissions")

finances = missil.make_rule(bearer, "finances")
finances_router = QualifiedRouter(rules=[finances.READ])

@finances_router.get("/finances/read")
async def finances_read_route() -> dict[str, str]:
    """Require read permission on finances."""
    return {"msg": "finances read access check via router rule!"}

@finances_router.get("/finances/write", dependencies=[finances.WRITE])
async def finances_write_route() -> dict[str, str]:
    """Require write permission on finances using an extra rule."""
    return {"msg": "finances write access check via extra qualified router rule!"}

app.include_router(finances_router)

if __name__ == "__main__":
    import uvicorn

    claims = {"userPermissions": {"finances": 1}}
    token = missil.encode_jwt_token(claims, SECRET_KEY, 8)

    print(f"add this token as an Authorization header: {token}")

    uvicorn.run(
        "qualified_router:app",
        port=8666,
        log_level="info",
        reload=True
    )
```

Grab the provided token above and make an HTTP request:

```python
import httpx

TOKEN = ""
client = httpx.Client()
url = "localhost:8666/finances/write"
headersList = {
 "Accept": "*/*",
 "User-Agent": "Thunder Client (https://www.thunderclient.com)",
 "Authorization": f"{TOKEN}" 
}

data = client.get(url, headers=headersList)
print(data.text)
```


## API Reference

### ::: missil.QualifiedRouter
