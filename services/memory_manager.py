from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, List

from engine.database import Database


class MemoryManager:
    """Lightweight in-memory + durable memory for agents."""

    def __init__(self, database: Database) -> None:
        self.database = database
        self._memory: DefaultDict[str, List[str]] = defaultdict(list)

    def remember(self, agent_id: str, item: str) -> None:
        self._memory[agent_id].append(item)
        self.database.record_event(f"memory::{agent_id}::{item[:64]}")

    def recall(self, agent_id: str) -> List[str]:
        return list(self._memory.get(agent_id, []))

    def clear(self, agent_id: str) -> None:
        self._memory.pop(agent_id, None)
        self.database.record_event(f"memory_clear::{agent_id}")

