from typing import Collection, Set

from fastapi import HTTPException
from starlette.authentication import AuthCredentials, BaseUser
from starlette.requests import HTTPConnection


class AuthCheckDependency:
    __slots__ = ("scopes",)

    def __init__(self, scopes: Collection[str]):
        self.scopes: Set[str] = {*scopes}

    def __call__(self, conn: HTTPConnection):
        user: BaseUser = conn.user
        if not user.is_authenticated:
            raise self._not_authenticated_error(conn, user)
        auth: AuthCredentials = conn.auth
        if not self.scopes.issubset(auth.scopes):
            raise self._not_authorized_error(conn, user, auth.scopes)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _not_authenticated_error(self, conn: HTTPConnection, user: BaseUser):
        return HTTPException(status_code=401)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _not_authorized_error(
        self, conn: HTTPConnection, user: BaseUser, scopes: Collection[str]
    ):
        return HTTPException(status_code=403)
