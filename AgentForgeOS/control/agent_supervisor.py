"""
Agent Supervisor
================
Coordinates multi-agent execution and enforces permission checks.
"""

from typing import Dict, Any, List
from .file_guard import assert_write_allowed


class AgentSupervisor:
    """Minimal supervisor enforcing write permissions before execution."""

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        target_paths = task.get("target_paths", [])
        assert_write_allowed(target_paths)
        record = {"task": task, "status": "approved"}
        self.audit_log.append(record)
        return record
