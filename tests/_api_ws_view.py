from typing import Optional

from fastapi import Header, WebSocket
from pydantic import BaseModel

from fastapi_ext.view import View, api, get, websocket


class StatusResult(BaseModel):
    ok: bool


class Request(BaseModel):
    request: str


class Result(BaseModel):
    result: str
    user_agent: str
    setting: str


class _WebSocketView(View):
    user_agent: Optional[str] = Header(None)

    def __init__(self, setting: str = "ws"):
        self.setting = setting

    async def _handle(self, ws: WebSocket):
        await ws.accept()
        while True:
            request_text = await ws.receive_text()
            request = Request.parse_raw(request_text)
            result = Result(
                result=f"result: {request.request}",
                user_agent=self.user_agent,
                setting=self.setting,
            )
            await ws.send_text(result.json())


@api("/ws-standalone")
class WebSocketStandaloneView(_WebSocketView):
    @websocket()
    async def handle(self, ws: WebSocket):
        await self._handle(ws)


@api("/ws-coexistence")
class WebSocketCoexistenceView(_WebSocketView):
    @websocket("/first")
    @websocket("/second")
    async def handle(self, ws: WebSocket):
        await self._handle(ws)

    @get("/status")
    async def status(self) -> StatusResult:
        return StatusResult(ok=True)
