"""Missil custom exceptions."""

import warnings

from fastapi import HTTPException


class PermissionDeniedException(HTTPException):
    """HTTP Exception raised on permission-related errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize a PermissionDeniedException.

        Parameters
        ----------
        status_code : int
            HTTP status code.
        detail : str
            Exception description.
        headers : dict[str, str], optional
            Response headers, by default {"WWW-Authenticate": "Bearer"}
        """
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}

        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenValidationException(HTTPException):
    """HTTP Exception raised on JWT token-related errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize a TokenValidationException.

        Parameters
        ----------
        status_code : int
            HTTP status code.
        detail : str
            Exception description.
        headers : dict[str, str], optional
            Response headers, by default {"WWW-Authenticate": "Bearer"}
        """
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}

        super().__init__(status_code=status_code, detail=detail, headers=headers)


_DEPRECATED: dict[str, str] = {
    "PermissionErrorException": "PermissionDeniedException",
    "TokenErrorException": "TokenValidationException",
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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
