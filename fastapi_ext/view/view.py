import inspect
from contextvars import ContextVar
from inspect import Signature
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
    get_type_hints,
)

from fastapi import APIRouter
from fastapi.params import Body, Depends, Param
from pydantic.typing import is_classvar

from fastapi_ext.view._utils import ClassMembers, desc_unwrap

_undefined = object()
_ParamTypeSet = (Param, Body, Depends)
_ParamType = Union[_ParamTypeSet]
_ctx = ContextVar("view_request_context", default=cast(Dict[str, Any], None))


class _CtxScope:
    __slots__ = "args", "token"

    def __init__(self, args: Dict[str, Any]):
        self.args = args
        self.token = None

    def __enter__(self):
        self.token = _ctx.set(self.args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _ctx.reset(self.token)
        self.token = None


class _ViewParam:
    __slots__ = "name", "hint", "param"

    def __init__(self, name: str, hint: Any, param: _ParamType):
        self.name = name
        self.hint = hint
        self.param = param

    def __get__(self, instance, owner):
        if instance is None:
            return self
        ctx = _ctx.get()
        if ctx is None:
            raise RuntimeError("Cannot get request property outside request context")
        try:
            return ctx[self.name]
        except KeyError:
            raise AssertionError(f"Request property {self.name} not set")

    def __set__(self, instance, value):
        raise TypeError("Cannot overwrite param property value")

    @classmethod
    def from_dependencies(
        cls, dependencies: Iterable[Tuple[str, Any, Any]]
    ) -> Iterator["_ViewParam"]:
        for name, hint, default in dependencies:
            yield _ViewParam(name, hint, default)


class _ViewCtxCatchFactory:
    @classmethod
    def create(cls, dependencies: Iterable[Tuple[str, Any, Any]]) -> Callable[..., Any]:
        def ctx_catch(**kwargs):
            return kwargs

        ctx_catch.__signature__ = Signature(
            parameters=[
                inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=default,
                    annotation=hint,
                )
                for name, hint, default in dependencies
            ]
        )
        return ctx_catch


class _ViewEndpoint:
    CTX_ARG = "__ctx__"

    def __init__(self, ctx_catch: Callable, attr_name: str, route_args: Dict[str, Any]):
        self.ctx_catch = ctx_catch
        self.attr_name = attr_name
        self.route_args = route_args

    def api_route_args(self, instance) -> Dict[str, Any]:
        method = getattr(instance, self.attr_name)
        func = desc_unwrap(method)
        signature = inspect.signature(method)

        endpoint_fn = self._endpoint_fn(method)
        endpoint_fn.__name__ = f"{type(instance).__name__}__{self.attr_name}"
        endpoint_fn.__doc__ = func.__doc__
        endpoint_fn.__signature__ = signature.replace(
            parameters=[
                *signature.parameters.values(),
                inspect.Parameter(
                    name=self.CTX_ARG,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(self.ctx_catch),
                ),
            ]
        )
        return {"endpoint": endpoint_fn, **self.route_args}

    @classmethod
    def _endpoint_fn(cls, method: Callable):
        ctx_arg = cls.CTX_ARG
        if inspect.iscoroutinefunction(method):

            async def _endpoint_fn(*args, **kwargs):
                with _CtxScope(kwargs.pop(ctx_arg)):
                    return await method(*args, **kwargs)

        else:

            def _endpoint_fn(*args, **kwargs):
                with _CtxScope(kwargs.pop(ctx_arg)):
                    return method(*args, **kwargs)

        return _endpoint_fn


class _ViewEndpointSetFactory:
    ROUTE_ARGS = "__route_args__"

    @classmethod
    def create(cls, clazz: Type, ctx_catch: Callable) -> Sequence[_ViewEndpoint]:
        return tuple(
            _ViewEndpoint(ctx_catch=ctx_catch, attr_name=name, route_args=route_args)
            for name, route_args in cls._method_routes(clazz)
        )

    @classmethod
    def _method_routes(cls, clazz: Type) -> Iterator[Tuple[str, Dict[str, Any]]]:
        for name, func in ClassMembers.all_class_fns(clazz):
            # only public methods
            if name.startswith("_"):
                continue
            route_args_set = _ViewEndpointRouteArgs.find(func)
            for route_args in route_args_set:
                yield name, route_args


class _ViewEndpointRouteArgs:
    ROUTE_ARGS = "__route_args__"

    @classmethod
    def find(cls, func) -> Collection[Dict[str, Any]]:
        func = desc_unwrap(func)
        func = inspect.unwrap(func, stop=cls._get)
        return cls._get(func)

    @classmethod
    def add(cls, func, args):
        func = desc_unwrap(func)
        route_args = cls._get(func)
        if not route_args:
            route_args = []
            setattr(func, cls.ROUTE_ARGS, route_args)
        route_args.append(args)

    @classmethod
    def _get(cls, fn) -> Collection[Dict[str, Any]]:
        return getattr(fn, cls.ROUTE_ARGS, ())


def _view_dependencies(clazz):
    for name, hint in get_type_hints(clazz).items():
        if is_classvar(hint):
            continue
        default = getattr(clazz, name, _undefined)
        if isinstance(default, _ParamTypeSet):
            yield name, hint, default
        if isinstance(default, _ViewParam):
            yield name, hint, default.param
        if default is ...:
            yield name, hint, default


class View:
    __router_args__: dict = {}
    __router__: Optional[APIRouter] = None
    __router_endpoints__: Sequence[_ViewEndpoint] = ()

    def __init_subclass__(cls, **kwargs):
        first_parent_view: Type[View] = next(
            c for c in cls.mro() if issubclass(c, View) and c is not cls
        )
        cls.__router_args__ = {**first_parent_view.__router_args__}

        dependencies = [*_view_dependencies(cls)]

        for param in _ViewParam.from_dependencies(dependencies):
            setattr(cls, param.name, param)

        ctx_catch = _ViewCtxCatchFactory.create(dependencies)
        cls.__router_endpoints__ = _ViewEndpointSetFactory.create(
            cls, ctx_catch=ctx_catch
        )

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
        for endpoint in self.__router_endpoints__:
            kwargs = endpoint.api_route_args(self)
            router.add_api_route(**kwargs)
