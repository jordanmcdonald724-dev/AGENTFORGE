"""
Background worker system placeholder.
"""

import asyncio
from typing import Callable, Awaitable


class WorkerSystem:
    """Runs background tasks asynchronously."""

    def __init__(self):
        self.tasks = []

    def schedule(self, coro: Awaitable):
        self.tasks.append(asyncio.create_task(coro))

    async def shutdown(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
