import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient, WebSocketTestSession

from tests._api_ws_view import (
    Request,
    Result,
    WebSocketCoexistenceView,
    WebSocketStandaloneView,
)


@pytest.fixture
def client() -> TestClient:
    standalone_router = WebSocketStandaloneView().router
    coexistence_router = WebSocketCoexistenceView().router
    app = FastAPI()
    app.include_router(standalone_router)
    app.include_router(coexistence_router, prefix="/prefix")
    return TestClient(app=app, base_url="http://localhost")


def _assert_ws_flow(client: TestClient, url: str):
    session: WebSocketTestSession = client.websocket_connect(url)
    for arg in ["first", "second"]:
        request = Request(request=arg)
        session.send_text(request.json())
        response_text = session.receive_text()
        result = Result.parse_raw(response_text)
        assert result.result == f"result: {request.request}"
        assert result.setting == "ws"
        assert "testclient" in result.user_agent
    session.close()


def test_standalone(client: TestClient):
    _assert_ws_flow(client, "/ws-standalone")


def test_coexistence(client: TestClient):
    response = client.get("/prefix/ws-coexistence/status")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True

    _assert_ws_flow(client, "/prefix/ws-coexistence/first")
    _assert_ws_flow(client, "/prefix/ws-coexistence/second")
