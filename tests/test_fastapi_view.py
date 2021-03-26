import httpx
import pytest
from fastapi import FastAPI

# noinspection PyProtectedMember
from fastapi_ext.view._routes import RouteEntryManager
from tests._view import ExampleView, OtherView


@pytest.fixture
def client() -> httpx.AsyncClient:
    example_router = ExampleView(setting="example").router
    other_router = OtherView(setting="other").router
    app = FastAPI()
    app.include_router(example_router)
    app.include_router(other_router)
    return httpx.AsyncClient(app=app, base_url="http://localhost")


def test_internals():
    assert ExampleView.__router_args__["tags"] == ["test"]
    assert OtherView.__router_args__["tags"] == ["test"]


@pytest.mark.parametrize(
    "url, params, setting",
    [
        ("/example-view", {}, "example"),
        ("/example-view", {"a": 10, "b": "test"}, "example"),
        ("/other-view", {"a": 5, "b": "other test"}, "other"),
    ],
)
@pytest.mark.asyncio
async def test_view_sync_get(
    client: httpx.AsyncClient, url: str, params: dict, setting: str
):
    async with client:
        response = await client.get(url, params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["a"] == params.get("a", 0)
        assert data["b"] == params.get("b", "")
        assert "httpx" in data["user_agent"]
        assert data["setting"] == setting


@pytest.mark.parametrize(
    "url, params, setting",
    [
        ("/example-view/nested-1", {}, "example"),
        ("/example-view/nested-2", {"a": 10, "b": "test"}, "example"),
    ],
)
@pytest.mark.asyncio
async def test_view_sync_get_nested(
    client: httpx.AsyncClient, url: str, params: dict, setting: str
):
    async with client:
        response = await client.get(url, params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["a"] == params.get("a", 0)
        assert data["b"] == params.get("b", "")


@pytest.mark.parametrize(
    "url, payload, setting",
    [
        ("/example-view", {"x": 1, "y": "test"}, "example"),
        ("/example-view/action", {"x": 1, "y": "test"}, "example"),
        ("/example-view/action-1", {"x": 10, "y": "test-1"}, "example"),
        ("/example-view/action-2", {"x": 20, "y": "test-2"}, "example"),
        ("/other-view", {"x": 5, "y": "other test"}, "other"),
    ],
)
@pytest.mark.asyncio
async def test_view_async_post(
    client: httpx.AsyncClient, url: str, payload: dict, setting: str
):
    async with client:
        response = await client.post(url, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"{payload['x']} {payload['y']} {setting}"
        assert "httpx" in data["user_agent"]


def test_view_response_model_infer():
    entries = RouteEntryManager.find(ExampleView.post_action)
    for entry in entries:
        assert entry.args["response_model"] is not None
