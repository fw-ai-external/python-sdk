from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, Generic, TypeVar, Callable, overload
from datetime import date, datetime
from typing_extensions import Self, Literal

import pydantic
from pydantic.fields import FieldInfo

from fireworks.training.sdk._core._types import IncEx, StrBytesIntFloat

_T = TypeVar("_T")
_ModelT = TypeVar("_ModelT", bound=pydantic.BaseModel)

# Native Pydantic 2 schema and HTTP helpers.

# Pyright incorrectly reports some of our functions as overriding a method when they don't
# pyright: reportIncompatibleMethodOverride=false


# Date/typing utilities provided by the installed Pydantic 2 package.
if TYPE_CHECKING:

    def parse_date(value: date | StrBytesIntFloat) -> date:  # noqa: ARG001
        ...

    def parse_datetime(value: Union[datetime, StrBytesIntFloat]) -> datetime:  # noqa: ARG001
        ...

    def get_args(t: type[Any]) -> tuple[Any, ...]:  # noqa: ARG001
        ...

    def is_union(tp: type[Any] | None) -> bool:  # noqa: ARG001
        ...

    def get_origin(t: type[Any]) -> type[Any] | None:  # noqa: ARG001
        ...

    def is_literal_type(type_: type[Any]) -> bool:  # noqa: ARG001
        ...

    def is_typeddict(type_: type[Any]) -> bool:  # noqa: ARG001
        ...

else:
    from pydantic.v1.typing import (
        get_args as get_args,
        is_union as is_union,
        get_origin as get_origin,
        is_typeddict as is_typeddict,
        is_literal_type as is_literal_type,
    )
    from pydantic.v1.datetime_parse import parse_date as parse_date, parse_datetime as parse_datetime


# refactored config
from pydantic import ConfigDict as ConfigDict


# renamed methods / properties
def parse_obj(model: type[_ModelT], value: object) -> _ModelT:
    return model.model_validate(value)


def field_get_default(field: FieldInfo) -> Any:
    value = field.get_default()
    from pydantic_core import PydanticUndefined

    if value == PydanticUndefined:
        return None
    return value


def get_model_fields(model: type[pydantic.BaseModel]) -> dict[str, FieldInfo]:
    return model.model_fields


def model_copy(model: _ModelT, *, deep: bool = False, update: dict[str, Any] | None = None) -> _ModelT:
    return model.model_copy(deep=deep, update=update)  # type: ignore


def model_dump(
    model: pydantic.BaseModel,
    *,
    exclude: IncEx | None = None,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    warnings: bool = True,
    mode: Literal["json", "python"] = "python",
) -> dict[str, Any]:
    return model.model_dump(
        mode=mode,
        exclude=exclude,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        warnings=warnings,
    )


# generic models
class GenericModel(pydantic.BaseModel): ...


# cached properties
if TYPE_CHECKING:
    cached_property = property

    # we define a separate type (copied from typeshed)
    # that represents that `cached_property` is `set`able
    # at runtime, which differs from `@property`.
    #
    # this is a separate type as editors likely special case
    # `@property` and we don't want to cause issues just to have
    # more helpful internal types.

    class typed_cached_property(Generic[_T]):
        func: Callable[[Any], _T]
        attrname: str | None

        def __init__(self, func: Callable[[Any], _T]) -> None: ...

        @overload
        def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

        @overload
        def __get__(self, instance: object, owner: type[Any] | None = None) -> _T: ...

        def __get__(self, instance: object, owner: type[Any] | None = None) -> _T | Self:
            raise NotImplementedError()

        def __set_name__(self, owner: type[Any], name: str) -> None: ...

        # __set__ is not defined at runtime, but @cached_property is designed to be settable
        def __set__(self, instance: object, value: _T) -> None: ...

else:
    from functools import cached_property as cached_property

    typed_cached_property = cached_property
