"""
Memory Manager
==============
Stores and retrieves conversation and project memory.
"""

from typing import Dict, List


class MemoryManager:
    def __init__(self):
        self._memory: Dict[str, List[Dict[str, str]]] = {}

    def append(self, key: str, entry: Dict[str, str]) -> None:
        self._memory.setdefault(key, []).append(entry)

    def history(self, key: str) -> List[Dict[str, str]]:
        return list(self._memory.get(key, []))
