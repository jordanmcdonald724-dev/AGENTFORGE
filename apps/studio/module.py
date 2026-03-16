from __future__ import annotations

from typing import Dict

from services.agent_service import AgentService


class StudioApp:
    """Surface level orchestration for the Studio UI."""

    def __init__(self, agent_service: AgentService) -> None:
        self.agent_service = agent_service

    async def kickoff(self, project_id: str, prompt: str) -> Dict[str, str]:
        await self.agent_service.dispatch_task(agent_id=f"studio::{project_id}", prompt=prompt)
        return {"project_id": project_id, "status": "scheduled"}

