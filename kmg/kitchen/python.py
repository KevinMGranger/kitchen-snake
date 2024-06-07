import enum
import inspect
from typing import (
    Callable,
    Generator,
    Generic,
    Iterator,
    TypeVar,
)

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
"""
A generic undefined singleton, for when `None` is semantically meaningful.
Can be nicely used as `Literal[UNDEFINED]`.
"""


def members(obj) -> list[str]:
    "list all public members (`__dir__`) of an object"
    return [member for member in dir(obj) if not member.startswith("_")]


class Unreachable(BaseException):
    "An exception for an unreachable branch."

    def __init__(self, message: str = "should be unreachable", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message


def todo(msg: str | None = None):
    raise NotImplementedError(msg) if msg is not None else NotImplementedError


# KeyType = TypeVar("KeyType", contravariant=True)
# SetType = TypeVar("SetType", contravariant=True)
# ReturnType = TypeVar("ReturnType", covariant=True)


# class SetitemAble(Protocol[KeyType, SetType]):
#     def __setitem__(self, key: KeyType, value: SetType, /):
#         ...


# class GetitemAble(Protocol[KeyType, ReturnType]):
#     def __getitem__(self, key: KeyType, /) -> ReturnType:
#         ...


# class GetSet(Protocol[KeyType, T]):
#     def __setitem__(self, key: KeyType, value: T, /):
#         ...

#     def __getitem__(self, key: KeyType, /) -> T:
#         ...


# @dc.dataclass
# class CollectionContext(Generic[KeyType, SetType]):
#     source: SetitemAble[KeyType, SetType]
#     key: KeyType

#     value: SetType

#     @classmethod
#     def from_collection(cls, source: GetSet[KeyType, SetType], key: KeyType):
#         return cls(source, key, source[key])

#     def update(self):
#         self.source[self.key] = self.value


YieldType = TypeVar("YieldType")
SendType = TypeVar("SendType")
ReturnType = TypeVar("ReturnType")


class Gen(
    Generic[YieldType, SendType, ReturnType],
    Iterator[YieldType],
):
    """
    Easily capture the return value of a generator,
    when otherwise used as an iterator.

    Usage:
    ```
    for x in (gen := Gen(some_generator_fn())):
        # something with x
        pass
    print(gen.ret)
    ```

    When the wrapped generator exits,
    its value will be available as the `ret` attribute.

    If you attempt to access `ret` before the generator exits,
    a `GeneratorNotFinishedError` will be raised.

    """

    UNFINISHED = object()

    @property
    def ret(self) -> ReturnType:
        if self._ret is self.UNFINISHED:
            raise GeneratorNotFinishedError
        else:
            return self._ret  # type: ignore

    # TODO: how to type that send can be anything as long as it includes None?
    def __init__(self, gen: Generator[YieldType, SendType | None, ReturnType]):
        self.gen = gen
        self._ret = self.UNFINISHED

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.gen)
        except StopIteration as e:
            self._ret = e.value
            raise


class GeneratorNotFinishedError(Exception):
    """
    Attempted to access the return value of a generator before
    it was finished.
    """

    pass


__all__ = ["inherit_default", "UNDEFINED", "Gen"]
