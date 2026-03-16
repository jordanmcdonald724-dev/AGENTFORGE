from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from control.ai_router import AIRouter
from control.file_guard import FileGuard


@dataclass
class AgentStatus:
    agent_id: str
    tasks_completed: int = 0
    violations: List[str] = field(default_factory=list)


class AgentSupervisor:
    """Coordinates AI agents and enforces repository safety rules."""

    def __init__(self, router: AIRouter, guard: FileGuard) -> None:
        self.router = router
        self.guard = guard
        self._agents: Dict[str, AgentStatus] = {}

    def register(self, agent_id: str) -> None:
        self._agents.setdefault(agent_id, AgentStatus(agent_id=agent_id))

    def record_completion(self, agent_id: str) -> None:
        self.register(agent_id)
        self._agents[agent_id].tasks_completed += 1

    def check_permission(self, agent_id: str, target_path: str) -> None:
        self.register(agent_id)
        try:
            self.guard.ensure_allowed(target_path)
        except PermissionError as exc:
            self._agents[agent_id].violations.append(str(exc))
            raise

    def route_task(self, task: str) -> str:
        routed = self.router.classify(task)
        if routed.protected:
            raise PermissionError("Task targets protected layer")
        return routed.route

    def snapshot(self) -> Dict[str, AgentStatus]:
        return self._agents

