import inspect
from types import FunctionType
from typing import Any, Iterator, Set, Tuple, Type, cast


def is_any_method(func) -> bool:
    return inspect.ismethod(func) or isinstance(func, (classmethod, staticmethod))


def desc_unwrap(func) -> FunctionType:
    if is_any_method(func):
        return cast(FunctionType, func.__func__)
    return func


class ClassMembers:
    @classmethod
    def all_class_fns(cls, obj: Type):
        for name, obj in cls.all_class_members(obj):
            if inspect.isfunction(obj):
                yield name, obj
            elif isinstance(obj, (classmethod, staticmethod)):
                yield name, obj.__func__

    @classmethod
    def all_class_members(cls, obj: Type) -> Iterator[Tuple[str, Any]]:
        visited: Set[str] = set()
        for clazz in cls._all_concrete_bases(obj):
            for name, obj in clazz.__dict__.items():
                if name in visited:
                    continue
                visited.add(name)
                yield name, obj

    @classmethod
    def _all_concrete_bases(cls, obj: Type) -> Iterator[Type]:
        for clazz in obj.mro():
            yield clazz
