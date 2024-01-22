from fastapi import HTTPException


class PermissionErrorException(HTTPException):
    """
    An HTTP exception you can raise in your own code to show errors to the client.

    Mainly for client errors, invalid authentication, invalid data, etc.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenErrorException(HTTPException):
    """HTTP Exception you can raise to show on JWT token-related errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
