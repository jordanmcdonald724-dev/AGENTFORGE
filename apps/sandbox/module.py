from __future__ import annotations

from typing import Dict

from control.agent_supervisor import AgentSupervisor


class SandboxApp:
    """Isolated sandbox for experimental features with safety checks."""

    def __init__(self, supervisor: AgentSupervisor) -> None:
        self.supervisor = supervisor

    def execute(self, agent_id: str, target_path: str) -> Dict[str, str]:
        self.supervisor.check_permission(agent_id, target_path)
        self.supervisor.record_completion(agent_id)
        return {"agent_id": agent_id, "path": target_path, "status": "allowed"}

