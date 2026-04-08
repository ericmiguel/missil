"""Simple FastAPI declarative endpoint-level access control."""

from missil._deprecated import make_deprecated_getattr
from missil.bearers import CookieTokenBearer
from missil.bearers import HeaderTokenBearer
from missil.bearers import TokenBearer
from missil.bearers import TokenSource
from missil.codec import decode_jwt_token
from missil.codec import encode_jwt_token
from missil.exceptions import PermissionDeniedException
from missil.exceptions import TokenValidationException
from missil.routers import ProtectedRouter
from missil.rules import ADMIN
from missil.rules import READ
from missil.rules import WRITE
from missil.rules import AccessRule
from missil.rules import Area
from missil.rules import AreasBase
from missil.rules import make_area
from missil.rules import make_areas
from missil.types import JWTClaims


__all__ = [
    "PermissionDeniedException",
    "TokenValidationException",
    "TokenSource",
    "encode_jwt_token",
    "decode_jwt_token",
    "CookieTokenBearer",
    "HeaderTokenBearer",
    "TokenBearer",
    "Area",
    "AreasBase",
    "AccessRule",
    "make_area",
    "make_areas",
    "ProtectedRouter",
    "READ",
    "WRITE",
    "ADMIN",
    "JWTClaims",
]

__getattr__ = make_deprecated_getattr(
    {
        "PermissionErrorException": "PermissionDeniedException",
        "TokenErrorException": "TokenValidationException",
        "FallbackTokenBearer": "TokenBearer",
        "FlexibleTokenBearer": "TokenBearer",
        "HTTPTokenBearer": "HeaderTokenBearer",
        "DENY": "ADMIN",
        "Scope": "Area",
        "Rule": "AccessRule",
        "make_scope": "make_area",
        "make_scopes": "make_areas",
        "make_rule": "make_area",
        "make_rules": "make_areas",
        "QualifiedRouter": "ProtectedRouter",
    },
    globals(),
    "missil",
)
