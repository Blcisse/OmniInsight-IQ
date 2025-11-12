from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Iterable, List, Optional


def convert_sync_to_async(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """Wrap a blocking/synchronous function to run in a thread for async use."""

    async def _runner(*args, **kwargs):
        try:
            # Python 3.9+: asyncio.to_thread
            return await asyncio.to_thread(func, *args, **kwargs)
        except AttributeError:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return _runner


def manage_event_loops() -> asyncio.AbstractEventLoop:
    """Return the current running loop, or create a new event loop if none.

    Useful in worker threads where no loop is set.
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def concurrent_task_queue(
    callables: Iterable[Callable[[], Awaitable[Any]]], *, concurrency: int = 5
) -> List[Any]:
    """Run async callables concurrently with a bounded semaphore.

    Returns list of results in submission order. Exceptions are propagated.
    """
    sem = asyncio.Semaphore(max(1, concurrency))
    results: List[Any] = [None] * len(list(callables))  # type: ignore
    tasks: List[asyncio.Task] = []

    async def _runner(idx: int, coro_factory: Callable[[], Awaitable[Any]]):
        async with sem:
            results[idx] = await coro_factory()

    for idx, factory in enumerate(callables):
        tasks.append(asyncio.create_task(_runner(idx, factory)))
    await asyncio.gather(*tasks)
    return results

