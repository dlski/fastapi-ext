from typing import Callable

from fastapi import Depends

from fastapi_ext.utils import AuthCheckDependency
from fastapi_ext.view.decorators.modify import (
    APIArgExtendDecorator,
    APIArgSetDecorator,
    ExtendDecoratedMember,
)


def depends(*dependencies) -> Callable[[ExtendDecoratedMember], ExtendDecoratedMember]:
    """
    Adds endpoint route or View subclass dependency
    :param dependencies: sequence of dependencies (`fastapi.Depends` argument)
    :return: function or class decorator
    """
    return APIArgExtendDecorator(
        *(Depends(d) for d in dependencies), name="dependencies"
    )


def authorized(
    *scopes: str,
) -> Callable[[ExtendDecoratedMember], ExtendDecoratedMember]:
    """
    Adds endpoint route or View subclass dependency,
    that checks is user authenticated and authorized within provided scopes.
    :param scopes: collection of scopes
    :return: function or class decorator
    """
    return depends(AuthCheckDependency(scopes))


def tags(*tags_: str) -> Callable[[ExtendDecoratedMember], ExtendDecoratedMember]:
    """
    Extends endpoint route or View subclass with tags
    :param tags_: sequence of tags
    :return: function or class decorator
    """
    return APIArgExtendDecorator(*tags_, name="tags")


def deprecated() -> Callable[[ExtendDecoratedMember], ExtendDecoratedMember]:
    """
    Mark endpoint route or View subclass API deprecated
    :return: function or class decorator
    """
    return APIArgSetDecorator(True, name="deprecated")
