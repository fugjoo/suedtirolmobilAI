"""Minimal subset of the :mod:`anyio` API used in tests.

This project only relies on :func:`run` to execute asynchronous callables.
The real `anyio` package offers a rich abstraction layer for asyncio and
other async libraries, but importing it would pull an additional dependency
which is unnecessary for the tests.  The lightweight implementation below
provides a compatible ``run`` function that either awaits a coroutine or
returns a regular value.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable


def run(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute ``func`` and return its result.

    If ``func`` returns a coroutine object it will be awaited using
    :func:`asyncio.run`.  Otherwise the value is returned directly.  This
    mirrors the behaviour expected by the tests and is sufficient for our
    needs.
    """

    result = func(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return asyncio.run(result)
    return result
