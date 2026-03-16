from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, List, Tuple


TaskFactory = Callable[[], Awaitable[None]]


class WorkerSystem:
    """Simple background task scheduler to keep the runtime extensible."""

    def __init__(self) -> None:
        self._tasks: List[Tuple[TaskFactory, float]] = []
        self._running: bool = False
        self._active_handles: List[asyncio.Task] = []

    def add_periodic_task(self, factory: TaskFactory, interval_seconds: float = 30.0) -> None:
        self._tasks.append((factory, interval_seconds))

    async def _runner(self, factory: TaskFactory, interval_seconds: float) -> None:
        while self._running:
            await factory()
            await asyncio.sleep(interval_seconds)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        for factory, interval in self._tasks:
            handle = asyncio.create_task(self._runner(factory, interval))
            self._active_handles.append(handle)

    async def shutdown(self) -> None:
        self._running = False
        for handle in self._active_handles:
            handle.cancel()
        self._active_handles.clear()

