import inspect
from typing import Any, Dict, Optional, Type, TypeVar, Union

from fastapi_ext.view import View
from fastapi_ext.view._routes import (
    APIRouteEntry,
    APIWebsocketRouteEntry,
    RouteEntryManager,
)
from fastapi_ext.view._utils import is_any_method
from fastapi_ext.view.decorators.types import MemberType

ExtendMemberType = Union[MemberType, type]
ExtendDecoratedMember = TypeVar("ExtendDecoratedMember", bound=ExtendMemberType)


class ModifyDecorator:
    def __call__(self, type_or_fn: ExtendDecoratedMember) -> ExtendDecoratedMember:
        if isinstance(type_or_fn, type):
            if not issubclass(type_or_fn, View) or type_or_fn is View:
                raise TypeError("Decorated class should be View subclass")
            self.extend_view(type_or_fn)
        elif inspect.isfunction(type_or_fn) or is_any_method(type_or_fn):
            self._extend_func(type_or_fn)
        else:
            raise TypeError(f"Not compatible type to decorate {type(type_or_fn)}")
        return type_or_fn

    def _extend_func(self, func: MemberType):
        for entry in RouteEntryManager.find(func):
            if isinstance(entry, APIRouteEntry):
                self.extend_api(entry)
            elif isinstance(entry, APIWebsocketRouteEntry):
                self.extend_api_websocket(entry)

    def extend_view(self, view_type: Type[View]):
        raise TypeError(
            f"Decorator {type(self).__name__} " f"do not support view extension"
        )

    def extend_api(self, entry: APIRouteEntry):
        raise TypeError(
            f"Decorator {type(self).__name__} " f"do not support API endpoint extension"
        )

    def extend_api_websocket(self, entry: APIWebsocketRouteEntry):
        raise TypeError(
            f"Decorator {type(self).__name__} "
            f"do not support API websocket endpoint extension"
        )


class APIArgModifyDecorator(ModifyDecorator):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        api_name: Optional[str] = None,
        view_name: Optional[str] = None,
    ):
        self.view_name = view_name or name
        self.api_name = api_name or name

    def extend_view(self, view_type: Type[View]):
        if self.view_name:
            self._modify(self.view_name, view_type.__router_args__)
        else:
            super().extend_view(view_type)

    def extend_api(self, entry: APIRouteEntry):
        if self.api_name:
            self._modify(self.api_name, entry.args)
        else:
            super().extend_api(entry)

    def _modify(self, name: str, args: Dict[str, Any]):
        raise NotImplementedError


class APIArgSetDecorator(APIArgModifyDecorator):
    def __init__(
        self,
        value: Any,
        *,
        name: Optional[str] = None,
        api_name: Optional[str] = None,
        view_name: Optional[str] = None,
    ):
        super().__init__(name=name, api_name=api_name, view_name=view_name)
        self.value = value

    def _modify(self, name: str, args: Dict[str, Any]):
        args[name] = self.value


class APIArgExtendDecorator(APIArgModifyDecorator):
    def __init__(
        self,
        *values: Any,
        name: Optional[str] = None,
        api_name: Optional[str] = None,
        view_name: Optional[str] = None,
    ):
        super().__init__(name=name, api_name=api_name, view_name=view_name)
        self.values = values

    def _modify(self, name: str, args: Dict[str, Any]):
        collection = args.get(name) or ()
        if not isinstance(collection, list):
            args[name] = collection = [*collection]
        collection.extend(self.values)
