import re
from typing import ClassVar, Collection, Optional, Sequence, Tuple, Type

from fastapi import APIRouter

from fastapi_ext.view._params import RequestCtxParam
from fastapi_ext.view._routes import RouteEntry, RouteEntryManager, RouteInstaller


class View:
    __router_args__: ClassVar[dict] = {}
    __router__: Optional[APIRouter] = None
    __route_entries__: ClassVar[Sequence[Tuple[str, RouteEntry]]] = ()
    __request_params__: ClassVar[Collection[RequestCtxParam]]
    __snake_name__: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs):
        first_parent_view: Type[View] = next(
            c for c in cls.mro() if issubclass(c, View) and c is not cls
        )
        cls.__router_args__ = {**first_parent_view.__router_args__}

        cls.__request_params__ = [*RequestCtxParam.from_class_attributes(cls)]
        for param in cls.__request_params__:
            setattr(cls, param.name, param)
        cls.__route_entries__ = [*RouteEntryManager.class_all(cls)]
        cls.__snake_name__ = cls.__get_snake_name__(cls.__name__)

    @classmethod
    def __get_snake_name__(cls, name: str):
        if name.endswith(View.__name__):
            name = name[: -len(View.__name__)]
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    @property
    def router(self) -> APIRouter:
        router = self.__router__
        if router is None:
            self.__router__ = router = self.__router_create__()
            self.__router_add_routes__(router)
        return router

    def __router_create__(self) -> APIRouter:
        return APIRouter(**self.__router_args__)

    def __router_add_routes__(self, router: APIRouter):
        ctx_catch = RequestCtxParam.ctx_catch_fn(self.__request_params__)
        installer = RouteInstaller(
            parent_snake_name=self.__snake_name__,
            ctx_catch=ctx_catch,
            router=router,
        )
        for name, entry in self.__route_entries__:
            method = getattr(self, name)
            installer.install(method=method, entry=entry, attr_name=name)
