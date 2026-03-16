"""
Agent Service
=============
Provides basic agent orchestration abstractions.
"""

from typing import Dict, Any, List
from providers.llm_provider import LLMProvider


class AgentService:
    """Coordinates prompts across provider-backed agents."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        return await self.llm.chat(prompt)
