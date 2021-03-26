import typing

from pydantic import BaseModel
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    BaseUser,
    SimpleUser,
    UnauthenticatedUser,
)
from starlette.requests import HTTPConnection

from fastapi_ext.view import View, api, authorized, deprecated, get, tags


class Result(BaseModel):
    result: str


TEST_SCOPE1 = "test-scope1"
TEST_SCOPE2 = "test-scope2"


TEST_SECRET1 = "test-secret1"
TEST_SECRET2 = "test-secret2"
TEST_SECRET3 = "test-secret3"

_SCOPE_MAP = {
    TEST_SECRET1: [],
    TEST_SECRET2: [TEST_SCOPE1],
    TEST_SECRET3: [TEST_SCOPE1, TEST_SCOPE2],
}


@api("/extras", tags=["test", "extras"])
class ExtrasView(View):
    @tags("free")
    @get("/free")
    def get_free(self) -> Result:
        return Result(result="free")

    @authorized()
    @get("/a-little-secured")
    def get_a_little_secured(self) -> Result:
        return Result(result="a-little-secured")

    @deprecated()
    @authorized(TEST_SCOPE1)
    @get("/partially-secured")
    def get_partial_secured(self) -> Result:
        return Result(result="partial-secured")

    @authorized(TEST_SCOPE1, TEST_SCOPE2)
    @get("/fully-secured")
    def get_fully_secured(self) -> Result:
        return Result(result="fully-secured")


@tags("test")
@tags("extras")
@authorized(TEST_SCOPE1, TEST_SCOPE2)
@api("/extras/whole")
class ExtrasWholeView(View):
    @get("/fully-secured")
    def get_fully_secured(self):
        return Result(result="whole-fully-secured")


class TestAuthenticationBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> typing.Optional[typing.Tuple[AuthCredentials, BaseUser]]:
        secret = conn.headers.get("secret")
        if secret in _SCOPE_MAP:
            scopes = _SCOPE_MAP[secret]
            return AuthCredentials(scopes), SimpleUser("smith")
        else:
            return AuthCredentials(), UnauthenticatedUser()
