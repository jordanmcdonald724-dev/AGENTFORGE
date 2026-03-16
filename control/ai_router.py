from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


TaskRoute = Literal["code_generation", "analysis", "research", "ops", "unknown"]


@dataclass
class RoutedTask:
    task: str
    route: TaskRoute
    protected: bool


class AIRouter:
    """Classifies tasks before they reach execution layers."""

    def __init__(self, protected_tasks: tuple[str, ...] = ("engine", "services", "providers", "control")) -> None:
        self.protected_tasks = protected_tasks

    def classify(self, task: str) -> RoutedTask:
        lowered = task.lower()
        if any(keyword in lowered for keyword in ("refactor", "modify", "write code")):
            route: TaskRoute = "code_generation"
        elif "research" in lowered:
            route = "research"
        elif any(keyword in lowered for keyword in ("deploy", "build", "ops")):
            route = "ops"
        elif any(keyword in lowered for keyword in ("analyze", "review", "inspect")):
            route = "analysis"
        else:
            route = "unknown"

        protected = any(keyword in lowered for keyword in self.protected_tasks)
        return RoutedTask(task=task, route=route, protected=protected)

