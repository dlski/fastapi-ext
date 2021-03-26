import pytest
from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.testclient import TestClient

from tests._api_extra import (
    TEST_SECRET1,
    TEST_SECRET2,
    TEST_SECRET3,
    ExtrasView,
    ExtrasWholeView,
    TestAuthenticationBackend,
)


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware, backend=TestAuthenticationBackend())
    app.include_router(ExtrasView().router)
    app.include_router(ExtrasWholeView().router)
    return TestClient(app=app, base_url="http://localhost")


@pytest.mark.parametrize(
    "suffix_url, secret, status_code",
    [
        ("/free", "", 200),
        ("/a-little-secured", "", 401),
        ("/a-little-secured", TEST_SECRET1, 200),
        ("/partially-secured", TEST_SECRET1, 403),
        ("/partially-secured", TEST_SECRET2, 200),
        ("/fully-secured", TEST_SECRET2, 403),
        ("/fully-secured", TEST_SECRET3, 200),
        ("/whole/fully-secured", "", 401),
        ("/whole/fully-secured", TEST_SECRET1, 403),
        ("/whole/fully-secured", TEST_SECRET3, 200),
    ],
)
def test_authorized(client: TestClient, suffix_url: str, secret: str, status_code: int):
    response = client.get(f"/extras{suffix_url}", headers={"secret": secret})
    print(response.text)
    assert response.status_code == status_code
