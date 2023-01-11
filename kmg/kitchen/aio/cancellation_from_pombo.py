# todo: need to compare these
import asyncio
from typing import TypeVar

# https://gist.github.com/twisteroidambassador/f35c7b17d4493d492fe36ab3e5c92202


class CancelledFromOutside(asyncio.CancelledError):
    pass


class CancelledFromInside(asyncio.CancelledError):
    pass


T = TypeVar("T")


async def distinguish_cancellation(fut: asyncio.Future[T]) -> T:
    """Wait for a future. If cancelled, raise different exceptions depending
    on who did the cancellation.
    If fut was cancelled, propagate cancellation outward by raising
    CancelledFromInside.
    If this function was cancelled, cancel fut, and raise CancelledFromOutside.
    """
    fut = asyncio.create_task(fut)  # TODO: why the type error?
    try:
        await asyncio.wait((fut,))
    except asyncio.CancelledError:
        # TODO: can we / do we need to optionally disable this?
        # will shielding fut cancel it, so we can leave it up to the caller?
        fut.cancel()
        raise CancelledFromOutside
    assert fut.done()
    if fut.cancelled():
        raise CancelledFromInside
    return fut.result()
