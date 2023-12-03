from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, TypeVar, cast
from datetime import date, datetime

import pydantic
from pydantic.fields import FieldInfo

from ._types import StrBytesIntFloat

_ModelT = TypeVar("_ModelT", bound=pydantic.BaseModel)

# --------------- Pydantic v2 compatibility ---------------

# Pyright incorrectly reports some of our functions as overriding a method when they don't
# pyright: reportIncompatibleMethodOverride=false

PYDANTIC_V2 = pydantic.VERSION.startswith("2.")

# v1 re-exports
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
    if PYDANTIC_V2:
        from pydantic.v1.typing import get_args as get_args
        from pydantic.v1.typing import is_union as is_union
        from pydantic.v1.typing import get_origin as get_origin
        from pydantic.v1.typing import is_typeddict as is_typeddict
        from pydantic.v1.typing import is_literal_type as is_literal_type
        from pydantic.v1.datetime_parse import parse_date as parse_date
        from pydantic.v1.datetime_parse import parse_datetime as parse_datetime
    else:
        from pydantic.typing import get_args as get_args
        from pydantic.typing import is_union as is_union
        from pydantic.typing import get_origin as get_origin
        from pydantic.typing import is_typeddict as is_typeddict
        from pydantic.typing import is_literal_type as is_literal_type
        from pydantic.datetime_parse import parse_date as parse_date
        from pydantic.datetime_parse import parse_datetime as parse_datetime


# refactored config
if TYPE_CHECKING:
    from pydantic import ConfigDict as ConfigDict
else:
    if PYDANTIC_V2:
        from pydantic import ConfigDict
    else:
        # TODO: provide an error message here?
        ConfigDict = None


# renamed methods / properties
def parse_obj(model: type[_ModelT], value: object) -> _ModelT:
    if PYDANTIC_V2:
        return model.model_validate(value)
    else:
        return cast(_ModelT, model.parse_obj(value))  # pyright: ignore[reportDeprecated, reportUnnecessaryCast]


def field_is_required(field: FieldInfo) -> bool:
    return field.is_required() if PYDANTIC_V2 else field.required


def field_get_default(field: FieldInfo) -> Any:
    value = field.get_default()
    if PYDANTIC_V2:
        from pydantic_core import PydanticUndefined

        return None if value == PydanticUndefined else value
    return value


def field_outer_type(field: FieldInfo) -> Any:
    return field.annotation if PYDANTIC_V2 else field.outer_type_


def get_model_config(model: type[pydantic.BaseModel]) -> Any:
    return model.model_config if PYDANTIC_V2 else model.__config__


def get_model_fields(model: type[pydantic.BaseModel]) -> dict[str, FieldInfo]:
    return model.model_fields if PYDANTIC_V2 else model.__fields__


def model_copy(model: _ModelT) -> _ModelT:
    return model.model_copy() if PYDANTIC_V2 else model.copy()


def model_json(model: pydantic.BaseModel, *, indent: int | None = None) -> str:
    if PYDANTIC_V2:
        return model.model_dump_json(indent=indent)
    return model.json(indent=indent)  # type: ignore


def model_dump(
    model: pydantic.BaseModel,
    *,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
) -> dict[str, Any]:
    if PYDANTIC_V2:
        return model.model_dump(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
        )
    return cast(
        "dict[str, Any]",
        model.dict(  # pyright: ignore[reportDeprecated, reportUnnecessaryCast]
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
        ),
    )


def model_parse(model: type[_ModelT], data: Any) -> _ModelT:
    return model.model_validate(data) if PYDANTIC_V2 else model.parse_obj(data)


# generic models
if not TYPE_CHECKING and PYDANTIC_V2 or TYPE_CHECKING:
    # there no longer needs to be a distinction in v2 but
    # we still have to create our own subclass to avoid
    # inconsistent MRO ordering errors
    class GenericModel(pydantic.BaseModel):
        ...

else:
    import pydantic.generics

    class GenericModel(pydantic.generics.GenericModel, pydantic.BaseModel):
        ...
