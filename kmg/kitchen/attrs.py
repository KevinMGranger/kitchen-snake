from typing import Any, Callable, Type, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def attrs_type_passthrough(
    type_: Type[T], converter: Callable[[U], V]
) -> Callable[[T | U], T | V]:
    """
    If an argument to an attrs converter is the given type,
    pass it through without modification.
    Otherwise, call the wrapped converter.
    """

    def _bingus(arg: T | U):
        if isinstance(arg, type_):
            return arg
        else:
            return converter(cast(U, arg))

    return _bingus


def simple_validator(c: Callable[[T], None]) -> Callable[[Any, Any, T], None]:
    """
    Take a simple one-argument validator, and wrap it to fit the
    attrs validator type signature.
    """
    return lambda _i, _a, v: c(v)
