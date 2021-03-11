import inspect
from types import FunctionType
from typing import cast


def desc_unwrap(func) -> FunctionType:
    if inspect.ismethod(func) or isinstance(func, (classmethod, staticmethod)):
        return cast(FunctionType, func.__func__)
    return func


def is_routine_or_call_desc(obj):
    return inspect.isroutine(obj) or isinstance(obj, (classmethod, staticmethod))
