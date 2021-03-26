import inspect
from typing import (
    Any,
    Callable,
    ClassVar,
    Collection,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Type,
)

from fastapi import APIRouter, Depends

from fastapi_ext.view._params import RequestCtx, RequestCtxCatchFn
from fastapi_ext.view._utils import ClassMembers, desc_unwrap

CallableType = Callable[..., Any]


class RouteEntry:
    def __init__(self, args: Dict[str, Any]):
        self.args = args

    def install(self, endpoint: CallableType, router: APIRouter):
        raise NotImplementedError


class APIRouteEntry(RouteEntry):
    def install(self, endpoint: CallableType, router: APIRouter):
        router.add_api_route(endpoint=endpoint, **self.args)


class APIWebsocketRouteEntry(RouteEntry):
    def install(self, endpoint: CallableType, router: APIRouter):
        # fix nested path for websocket routes
        args = {**self.args, "path": f"{router.prefix}{self.args['path']}"}
        # add api websocket route
        router.add_api_websocket_route(endpoint=endpoint, **args)


class RouteEntryManager:
    prop_name: ClassVar[str] = "_route_entries"

    @classmethod
    def find(cls, func: CallableType) -> Collection[RouteEntry]:
        func = desc_unwrap(func)
        func = inspect.unwrap(func, stop=cls._get)
        return cls._get(func)

    @classmethod
    def add(cls, func: CallableType, entry: RouteEntry):
        func = desc_unwrap(func)
        route_args = cls._get(func)
        if not route_args:
            route_args = []
            setattr(func, cls.prop_name, route_args)
        route_args.append(entry)

    @classmethod
    def _get(cls, fn: CallableType) -> Collection[RouteEntry]:
        return getattr(fn, cls.prop_name, ())

    @classmethod
    def class_all(cls, clazz: Type) -> Iterable[Tuple[str, RouteEntry]]:
        for name, func in ClassMembers.all_class_fns(clazz):
            # only public methods
            if name.startswith("_"):
                continue
            for entry in cls.find(func):
                yield name, entry


class RouteEndpointFactory:
    ctx_arg_name: ClassVar[str] = "__ctx__"

    def __init__(self, parent_snake_name: str, ctx_catch: RequestCtxCatchFn):
        self.parent_snake_name = parent_snake_name
        self.ctx_catch = ctx_catch

    def from_method(
        self, method: Callable[..., Any], attr_name: Optional[str] = None
    ) -> CallableType:
        signature = inspect.signature(method)
        func = desc_unwrap(method)
        attr_name = attr_name or func.__name__

        endpoint_fn = self._endpoint_body(method)
        endpoint_fn.__name__ = f"{self.parent_snake_name}__{attr_name}"
        endpoint_fn.__doc__ = func.__doc__
        endpoint_fn.__signature__ = signature.replace(
            parameters=[
                *signature.parameters.values(),
                inspect.Parameter(
                    name=self.ctx_arg_name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(self.ctx_catch),
                ),
            ]
        )
        return endpoint_fn

    @classmethod
    def _endpoint_body(cls, cb: Callable[..., Any]) -> Callable[..., Any]:
        assert callable(cb), "Provided object is not callable"
        arg_name = cls.ctx_arg_name
        # noinspection PyUnresolvedReferences
        routine = cb if inspect.isroutine(cb) else cb.__call__
        if inspect.iscoroutinefunction(routine):

            async def _endpoint_fn(*args, **kwargs):
                with RequestCtx(kwargs.pop(arg_name)):
                    return await cb(*args, **kwargs)

        else:

            def _endpoint_fn(*args, **kwargs):
                with RequestCtx(kwargs.pop(arg_name)):
                    return cb(*args, **kwargs)

        return _endpoint_fn


class RouteInstaller:
    def __init__(self, endpoint_factory: RouteEndpointFactory, router: APIRouter):
        self.endpoint_factory = endpoint_factory
        self.router = router

    def install(
        self,
        method: Callable[..., Any],
        entry: RouteEntry,
        attr_name: Optional[str] = None,
    ):
        endpoint_fn = self.endpoint_factory.from_method(
            method=method, attr_name=attr_name
        )
        entry.install(endpoint=endpoint_fn, router=self.router)
