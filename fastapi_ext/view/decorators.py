import inspect
from functools import update_wrapper
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

from fastapi import params
from fastapi.datastructures import Default
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.routing import APIRoute
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp

from fastapi_ext.view._utils import desc_unwrap
from fastapi_ext.view.view import View, _ViewEndpointRouteArgs

MemberType = Union[Callable[..., Any], classmethod, staticmethod]
DecoratedMember = TypeVar("DecoratedMember", bound=MemberType)


def _wrap_api(fn):
    # noinspection PyShadowingNames
    def api(*args, **kwargs):
        def decorator(type_):
            if (
                not isinstance(type_, type)
                or not issubclass(type_, View)
                or type_ is View
            ):
                raise TypeError("Decorator should be applied to View subclass")
            if "prefix" not in kwargs:
                if len(args) > 1:
                    raise TypeError(
                        f"TypeError: api() takes 1 "
                        f"positional arguments but {len(args)} was given"
                    )
                kwargs["prefix"] = args[0] if args else ""
            type_.__router_args__.update(kwargs)
            return type_

        return decorator

    update_wrapper(api, fn)
    return api


@_wrap_api
def api(
    prefix: str = "",
    *,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    default_response_class: Type[Response] = Default(JSONResponse),
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    routes: Optional[List[routing.BaseRoute]] = None,
    redirect_slashes: bool = True,
    default: Optional[ASGIApp] = None,
    dependency_overrides_provider: Optional[Any] = None,
    route_class: Type[APIRoute] = APIRoute,
    on_startup: Optional[Sequence[Callable[[], Any]]] = None,
    on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
    deprecated: Optional[bool] = None,
    include_in_schema: bool = True,
):
    _ = locals()

    def decorator(_):
        raise AssertionError("api decorator not wrapped")

    return decorator


def route(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    methods: Optional[List[str]] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    args = dict(locals())

    def decorator(member: MemberType) -> MemberType:
        if not inspect.isroutine(member):
            raise TypeError("Decorator should be applied to routine")
        # infer response_model from function return type hint
        infer = args.pop("response_model_infer")
        if infer and args["response_model"] is None:
            args["response_model"] = get_type_hints(desc_unwrap(member)).get("return")
        # add route args
        _ViewEndpointRouteArgs.add(member, args)
        return member

    return decorator


def get(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["GET"])


def put(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["PUT"])


def post(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["POST"])


def delete(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["DELETE"])


def options(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["OPTIONS"])


def head(
    self,
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["HEAD"])


def patch(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["PATCH"])


def trace(
    path: str = "",
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    response_model_infer: bool = True,
) -> Callable[[DecoratedMember], DecoratedMember]:
    return route(**locals(), methods=["TRACE"])
