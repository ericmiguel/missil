"""Simple FastAPI declarative endpoint-level access control."""

import warnings

from missil.bearers import CookieTokenBearer
from missil.bearers import FallbackTokenBearer
from missil.bearers import HeaderTokenBearer
from missil.bearers import TokenSource
from missil.exceptions import PermissionDeniedException
from missil.exceptions import TokenValidationException
from missil.jwt_utilities import decode_jwt_token
from missil.jwt_utilities import encode_jwt_token
from missil.routers import ProtectedRouter
from missil.rules import DENY
from missil.rules import READ
from missil.rules import WRITE
from missil.rules import AccessRule
from missil.rules import Scope
from missil.rules import make_scope
from missil.rules import make_scopes


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
]

_DEPRECATED: dict[str, str] = {
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
}


def __getattr__(name: str) -> object:
    if name in _DEPRECATED:
        new_name = _DEPRECATED[name]
        warnings.warn(
            f"'{name}' is deprecated and will be removed in a future version. "
            f"Use '{new_name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_name]
    raise AttributeError(f"module 'missil' has no attribute {name!r}")
