#!/usr/bin/env python3
"""ziro-shell — async helpers.

Layer: 3 (Python core, cold-path only)
Spec: 008

Provides asyncio utilities for parallel analysis and cold-path I/O operations.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Awaitable, Callable, Iterable, TypeVar

T = TypeVar("T")

DEFAULT_TIMEOUT_S = 5.0
DEFAULT_CONCURRENCY = 8


async def gather_bounded(
    coros: Iterable[Awaitable[T]],
    *,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> list[T]:
    """Run awaitables with bounded concurrency.

    Returns results in original order. Exceptions are propagated
    (caller should handle).
    """
    sem = asyncio.Semaphore(concurrency)

    async def _run(coro: Awaitable[T]) -> T:
        async with sem:
            return await coro

    return await asyncio.gather(*(_run(c) for c in coros))


async def with_timeout(
    coro: Awaitable[T],
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    on_timeout: Callable[[], T] | None = None,
) -> T:
    """Run with timeout; return fallback on timeout if provided."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_s)
    except asyncio.TimeoutError:
        if on_timeout is None:
            raise
        return on_timeout()


def run(coro: Awaitable[T]) -> T:
    """Synchronous entry point for CLI-invoked async code."""
    try:
        return asyncio.run(coro)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)


__all__ = [
    "gather_bounded",
    "with_timeout",
    "run",
    "DEFAULT_TIMEOUT_S",
    "DEFAULT_CONCURRENCY",
]
