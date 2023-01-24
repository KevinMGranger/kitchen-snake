import inspect
import enum
from typing import Callable, TypeVar, Generic, Protocol
from collections.abc import MutableSequence
import dataclasses as dc

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

KeyType = TypeVar("KeyType", contravariant=True)
SetType = TypeVar("SetType", contravariant=True)
ReturnType = TypeVar("ReturnType", covariant=True)


class SetitemAble(Protocol[KeyType, SetType]):
    def __setitem__(self, key: KeyType, value: SetType, /):
        ...


class GetitemAble(Protocol[KeyType, ReturnType]):
    def __getitem__(self, key: KeyType, /) -> ReturnType:
        ...


class GetSet(Protocol[KeyType, T]):
    def __setitem__(self, key: KeyType, value: T, /):
        ...

    def __getitem__(self, key: KeyType, /) -> T:
        ...


@dc.dataclass
class CollectionContext(Generic[KeyType, SetType]):
    source: SetitemAble[KeyType, SetType]
    key: KeyType

    value: SetType

    @classmethod
    def from_collection(cls, source: GetSet[KeyType, SetType], key: KeyType):
        return cls(source, key, source[key])

    def update(self):
        self.source[self.key] = self.value


__all__ = ["inherit_default", "UNDEFINED", "CollectionContext"]
