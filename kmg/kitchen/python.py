import inspect
import enum
from typing import Callable, TypeVar

T = TypeVar("T")


def inherit_default(func: Callable, param: str, type_: type[T]) -> T:
    """
    Inherit the default value from another function's parameter.
    Useful for APIs that wrap other APIs.
    """
    if (
        default := inspect.signature(func).parameters[param].default
    ) is inspect.Parameter.empty:
        raise ValueError(f"parameter {param} did not have a default")
    elif not isinstance(default, type_):
        raise TypeError(f"parameter {param} did not have the right type")
    else:
        return default


class Undefined(enum.Enum):
    UNDEFINED = enum.auto()


UNDEFINED = Undefined.UNDEFINED
