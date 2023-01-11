from typing import Awaitable, Callable
import pytest
from kmg.kitchen.aio import (
    CancelledFromInside,
    CancelledFromOutside,
    distinguish_cancellation,
)
import asyncio

# TODO: test composition with signal handling

async def with_logging_cancellation(task: Awaitable):
    try:
        await task
    except CancelledFromInside:
        print("inside")
        raise
    except CancelledFromOutside:
        print("outside")
        raise
    except asyncio.CancelledError:
        print("general cancelled")
        raise


@pytest.mark.asyncio
async def test_cancel_inner_task():
    event = asyncio.Event()
    event_task = asyncio.create_task(event.wait())

    async def outer():
        with pytest.raises(CancelledFromInside):
            await with_logging_cancellation(distinguish_cancellation(event_task))

    event_task.cancel()
    await outer()


@pytest.mark.asyncio
async def test_cancel_outer_task():
    event = asyncio.Event()
    sleeper = asyncio.create_task(event.wait())

    async def outer():
        with pytest.raises(CancelledFromOutside):
            await with_logging_cancellation(distinguish_cancellation(sleeper))

    outer_task = asyncio.create_task(outer())
    await asyncio.sleep(0)  # is this really guaranteed to make sure it's scheduled?
    outer_task.cancel()

    await outer_task


@pytest.mark.asyncio
async def test_cancel_inner_future():
    event = asyncio.Event()
    event_task = asyncio.create_task(event.wait())

    async def nested_inner():
        await event_task

    async def outer():
        with pytest.raises(CancelledFromInside):
            await with_logging_cancellation(distinguish_cancellation(nested_inner()))
    
    event_task.cancel()
    await outer()
