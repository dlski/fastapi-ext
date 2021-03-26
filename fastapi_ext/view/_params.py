import inspect
from contextvars import ContextVar
from inspect import Signature
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    Type,
    Union,
    cast,
    get_type_hints,
)

from fastapi.params import Body, Depends, Param
from pydantic.typing import is_classvar

_undefined = object()
_ctx = ContextVar("view_request_context", default=cast(Dict[str, Any], None))
ParamTypeSet = (Param, Body, Depends)

ParamType = Union[ParamTypeSet]
RequestCtxCatchFn = Callable[..., Dict[str, Any]]


class RequestCtx:
    __slots__ = "args", "token"

    def __init__(self, args: Dict[str, Any]):
        self.args = args
        self.token = None

    def __enter__(self):
        self.token = _ctx.set(self.args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _ctx.reset(self.token)
        self.token = None


class RequestCtxParam:
    __slots__ = "name", "hint", "param"

    def __init__(self, name: str, hint: Any, param: ParamType):
        assert isinstance(name, str)
        assert isinstance(param, ParamTypeSet)
        self.name = name
        self.hint = hint
        self.param = param

    def clone(self):
        return RequestCtxParam(self.name, self.hint, self.param)

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
    def from_class_attributes(cls, clazz: Type) -> Iterable["RequestCtxParam"]:
        for name, hint in get_type_hints(clazz).items():
            if is_classvar(hint):
                continue
            value = getattr(clazz, name, _undefined)
            if isinstance(value, ParamTypeSet):
                yield RequestCtxParam(name, hint, value)
            elif isinstance(value, RequestCtxParam):
                yield value.clone()
            elif value is ...:
                yield RequestCtxParam(name, hint, ...)

    @classmethod
    def ctx_catch_fn(cls, params: Collection["RequestCtxParam"]) -> RequestCtxCatchFn:
        def ctx_catch(**kwargs):
            return kwargs

        ctx_catch.__signature__ = Signature(
            parameters=[
                inspect.Parameter(
                    name=param.name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=param.param,
                    annotation=param.hint,
                )
                for param in params
            ]
        )
        return ctx_catch
