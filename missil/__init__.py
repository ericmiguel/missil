"""
Simple FastAPI declarative endpoint-level access control.

Scopes did not meet needs and other permission systems were too complex, so I designed
this code for my and my team needs, but feel free to use it if you like.
"""

import json

from typing import Annotated

from fastapi import Depends as FastAPIDependsFunc
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.params import Depends as FastAPIDependsClass
from pydantic import BaseModel


READ = 0
WRITE = 1
DENY = -1


class PrivilegeBearer:
    """
    Read current user privileges com (http-only) Cookies.

    Almost the same as 'OAuth2PasswordBearer' from FastAPI, but targets cookies by
    a key, not a token from an Oauth2 URL.
    """

    def __init__(self, key: str):
        self.key = key

    async def __call__(self, request: Request) -> BaseModel:
        policies = request.cookies.get(self.key)

        if not policies:
            raise ValueError(
                f"User privileges cookies not found using key '{self.key}'"
            )

        return json.loads(policies)


class PolicyException(HTTPException):
    """
    An HTTP exception you can raise in your own code to show errors to the client.

    This is for client errors, invalid authentication, invalid data, etc.
    Not for server errors in your code.
    """
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def get_current_user_privileges(key: str = "UserPrivileges") -> PrivilegeBearer:
    "Get a Bearer instance. Just a syntactic sugar."
    return PrivilegeBearer(key)


class Permission(FastAPIDependsClass):
    """FastAPI dependency to set endpoint-level access rules."""
    
    def __init__(
        self,
        area: str,
        level: int,
        policy_bearer: PrivilegeBearer | None = None,
        use_cache: bool = True,
    ):
        """
         Set an area and access level to deny or allow user access to and endpoint.

        Parameters
        ----------
        area : str
            business area name like 'financial' or 'human resources'.
        level : int
            access level, like 'read', 'write', etc.
        policy_bearer : PrivilegeBearer | Any | None
            current user privilegies source. You can create a custom bearer and get
            values from your DB, or whatever.
        use_cache : bool, optional
            FastAPI Depends class parameter, by default True
        """        
        self.area = area
        self.level = level
        self.use_cache = use_cache
        self.policy_bearer = policy_bearer

        if not self.policy_bearer:
            self.policy_bearer = get_current_user_privileges()

    @property
    def dependency(self):
        """Allows Missil to pass a FastAPI dependency that gets correctly evaluated."""

        def check_user_privileges(
            policies: Annotated[dict[str, int], FastAPIDependsFunc(self.policy_bearer)]
        ):
            if not self.area in policies:
                raise PolicyException(
                    status.HTTP_403_FORBIDDEN, f"'{self.area}' not in user privileges."
                )

            if not policies[self.area] >= self.level:
                raise PolicyException(
                    status.HTTP_403_FORBIDDEN,
                    "insufficient access level: "
                    f"({policies[self.area]}/{self.level}) on {self.area}.",
                )

        return check_user_privileges
