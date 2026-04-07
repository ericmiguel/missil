"""Missil custom exceptions."""

from fastapi import HTTPException

from missil._deprecated import make_deprecated_getattr


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


__getattr__ = make_deprecated_getattr(
    {
        "PermissionErrorException": "PermissionDeniedException",
        "TokenErrorException": "TokenValidationException",
    },
    globals(),
    __name__,
)
