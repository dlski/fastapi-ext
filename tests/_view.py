from typing import Optional

from fastapi import Body, Depends, Header
from pydantic import BaseModel

from fastapi_ext.view import View, api, get, post


class _QueryParams(BaseModel):
    a: int = 0
    b: str = ""


class _QueryResult(BaseModel):
    a: int
    b: str


class _RichQueryResult(_QueryResult):
    user_agent: Optional[str]
    setting: str


class _ActionPayload(BaseModel):
    x: int
    y: str


class _ActionResult(BaseModel):
    message: str
    user_agent: str


@api("/example-view", tags=["test"])
class ExampleView(View):
    user_agent: Optional[str] = Header(None)

    def __init__(self, setting: str):
        self.setting = setting

    @get()
    def query(self, params: _QueryParams = Depends()):
        return _RichQueryResult(
            a=params.a,
            b=params.b,
            user_agent=self._prepare_user_agent(),
            setting=self.setting,
        )

    # noinspection PyNestedDecorators
    @get("/nested-1")
    @classmethod
    def nested_cls_query(cls, params: _QueryParams = Depends()) -> _QueryResult:
        return _QueryResult(**params.dict())

    # noinspection PyNestedDecorators
    @get("/nested-2")
    @staticmethod
    def nested_static_query(params: _QueryParams = Depends()) -> _QueryResult:
        return _QueryResult(**params.dict())

    @post()
    async def post_action(self, payload: _ActionPayload = Body(...)) -> _ActionResult:
        return _ActionResult(
            message=f"{payload.x} {payload.y} {self.setting}",
            user_agent=self._prepare_user_agent(),
        )

    @post("/action")
    async def nested_post_action(
        self, payload: _ActionPayload = Body(...)
    ) -> _ActionResult:
        return await self.post_action(payload)

    @post("/action-1")
    @post("/action-2")
    async def double_post_action(
        self, payload: _ActionPayload = Body(...)
    ) -> _ActionResult:
        return await self.post_action(payload)

    def _prepare_user_agent(self) -> str:
        return self.user_agent or ""


@api("/other-view")
class OtherView(ExampleView):
    pass
