"""Simple FastAPI declarative endpoint-level access control."""

from missil._deprecated import make_deprecated_getattr
from missil.bearers import CookieTokenBearer
from missil.bearers import FallbackTokenBearer
from missil.bearers import HeaderTokenBearer
from missil.bearers import TokenSource
from missil.codec import decode_jwt_token
from missil.codec import encode_jwt_token
from missil.exceptions import PermissionDeniedException
from missil.exceptions import TokenValidationException
from missil.routers import ProtectedRouter
from missil.rules import DENY
from missil.rules import READ
from missil.rules import WRITE
from missil.rules import AccessRule
from missil.rules import Scope
from missil.rules import make_scope
from missil.rules import make_scopes
from missil.types import JWTClaims


__all__ = [
    "PermissionDeniedException",
    "TokenValidationException",
    "TokenSource",
    "encode_jwt_token",
    "decode_jwt_token",
    "CookieTokenBearer",
    "HeaderTokenBearer",
    "FallbackTokenBearer",
    "Scope",
    "AccessRule",
    "make_scope",
    "make_scopes",
    "ProtectedRouter",
    "READ",
    "WRITE",
    "DENY",
    "JWTClaims",
]

__getattr__ = make_deprecated_getattr(
    {
        "PermissionErrorException": "PermissionDeniedException",
        "TokenErrorException": "TokenValidationException",
        "TokenBearer": "TokenSource",
        "HTTPTokenBearer": "HeaderTokenBearer",
        "FlexibleTokenBearer": "FallbackTokenBearer",
        "Area": "Scope",
        "Rule": "AccessRule",
        "make_rule": "make_scope",
        "make_rules": "make_scopes",
        "QualifiedRouter": "ProtectedRouter",
    },
    globals(),
    "missil",
)
