from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from engine.worker_system import WorkerSystem
from providers.llm_provider import LLMProvider
from .memory_manager import MemoryManager


class AgentService:
    """Coordinates multi-agent orchestration using configured providers."""

    def __init__(
        self,
        worker_system: WorkerSystem,
        memory: MemoryManager,
        llm_provider: Optional[LLMProvider] = None,
    ) -> None:
        self.worker_system = worker_system
        self.memory = memory
        self.llm_provider = llm_provider

    async def dispatch_task(self, agent_id: str, prompt: str) -> Dict[str, str]:
        """Run an agent task asynchronously and persist a memory trace."""
        async def _execute() -> None:
            response = prompt
            if self.llm_provider:
                response = await self.llm_provider.chat([{"role": "user", "content": prompt}])
            self.memory.remember(agent_id, response)

        await asyncio.gather(_execute())
        return {"agent_id": agent_id, "status": "scheduled"}

    async def broadcast(self, agent_ids: List[str], prompt: str) -> List[Dict[str, str]]:
        return await asyncio.gather(*(self.dispatch_task(agent, prompt) for agent in agent_ids))

