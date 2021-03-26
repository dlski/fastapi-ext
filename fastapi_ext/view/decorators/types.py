from typing import Any, Callable, TypeVar

MemberType = Callable[..., Any]
DecoratedMember = TypeVar("DecoratedMember", bound=MemberType)
