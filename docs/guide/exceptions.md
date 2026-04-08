# Exceptions

Both Missil exceptions are subclasses of FastAPI's `HTTPException`, so FastAPI
catches and serializes them automatically — no extra configuration needed.

## When each exception is raised

| Exception | Raised by | Typical cause |
|---|---|---|
| `TokenValidationException` | Bearer (token extraction) | Missing, expired, or tampered token |
| `PermissionDeniedException` | AccessRule (permission check) | Area not in claims, or insufficient level |

## Raising exceptions manually

`PermissionDeniedException` can be raised directly in your own code to block
access based on custom logic. In this example `areas.finances.READ` is an
[`AccessRule`](access-control.md#declaring-areas-with-areasbase), and `AppClaims`
is a subclass of [`JWTClaims`](bearers.md#working-with-jwt-claims):

```python
from fastapi import status
from missil.exceptions import PermissionDeniedException

@app.get("/report", dependencies=[areas.finances.READ])
def report(user: Annotated[AppClaims, areas.finances.READ]) -> dict:
    if user.get("is_suspended"):
        raise PermissionDeniedException(
            status.HTTP_403_FORBIDDEN,
            "Account suspended.",
        )
    return {"data": "..."}
```

## Customizing the response format

Register a FastAPI exception handler to override the default JSON response:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from missil.exceptions import PermissionDeniedException, TokenValidationException


@app.exception_handler(PermissionDeniedException)
async def permission_denied_handler(request: Request, exc: PermissionDeniedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "forbidden", "message": exc.detail},
    )


@app.exception_handler(TokenValidationException)
async def token_validation_handler(request: Request, exc: TokenValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "unauthorized", "message": exc.detail},
    )
```

---

**See also:**

- [Access Control guide](access-control.md) — rules and areas that trigger these exceptions
- [Bearers guide](bearers.md) — when `TokenValidationException` is raised during token extraction
- [API Reference → Exceptions](../reference/exceptions.md) — `PermissionDeniedException`, `TokenValidationException`
