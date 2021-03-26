from fastapi_ext.view._view import View
from fastapi_ext.view.decorators import (
    api,
    delete,
    get,
    head,
    options,
    patch,
    post,
    put,
    route,
    trace,
    websocket,
)
from fastapi_ext.view.decorators.extra import authorized, depends, deprecated, tags

__all__ = [
    # view
    "View",
    # view decorator
    "api",
    # endpoint decorators
    "route",
    "websocket",
    "get",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
    # extensions decorators
    "authorized",
    "depends",
    "deprecated",
    "tags",
]
