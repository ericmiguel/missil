"""Missil custom exceptions."""

from fastapi import HTTPException


class PermissionErrorException(HTTPException):
    """HTTP Exception you can raise to show on permission-related errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize a PermissionErrorException.

        Parameters
        ----------
        status_code : int
            HTTP status code.
        detail : str
            Exception description.
        headers : _type_, optional
            Response headers, by default {"WWW-Authenticate": "Bearer"}
        """
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}

        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenErrorException(HTTPException):
    """HTTP Exception you can raise to show on JWT token-related errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize a TokenErrorException.

        Parameters
        ----------
        status_code : int
            HTTP status code.
        detail : str
            Exception description.
        headers : _type_, optional
            Response headers, by default {"WWW-Authenticate": "Bearer"}
        """
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}

        super().__init__(status_code=status_code, detail=detail, headers=headers)
