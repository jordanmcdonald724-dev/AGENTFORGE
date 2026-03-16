"""
AI Router
=========
Classifies inbound AI tasks and routes them to the correct app/service while
respecting the control layer policies.
"""

from typing import Dict, Any

PROTECTED_DIRECTORIES = {"engine", "services", "providers", "control"}


def route_task(task: Dict[str, Any]) -> str:
    """
    Minimal router that returns a target subsystem name.
    Future implementations can apply ML-based classification.
    """
    domain = task.get("domain", "general")
    if domain in {"deploy", "build"}:
        return "apps.builds"
    if domain in {"research", "knowledge"}:
        return "apps.research"
    return "apps.studio"
