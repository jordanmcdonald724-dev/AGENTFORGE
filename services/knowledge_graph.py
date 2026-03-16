from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, List, Set


class KnowledgeGraphService:
    """Stores relationships between entities discovered across the system."""

    def __init__(self) -> None:
        self._edges: DefaultDict[str, Set[str]] = defaultdict(set)
        self._attributes: Dict[str, Dict[str, str]] = {}

    def add_edge(self, source: str, target: str) -> None:
        self._edges[source].add(target)

    def add_attributes(self, node: str, attributes: Dict[str, str]) -> None:
        self._attributes[node] = {**self._attributes.get(node, {}), **attributes}

    def neighbors(self, node: str) -> List[str]:
        return sorted(self._edges.get(node, set()))

    def describe(self, node: str) -> Dict[str, str]:
        return self._attributes.get(node, {})

    def snapshot(self) -> Dict[str, Dict[str, List[str]]]:
        return {
            "edges": {node: sorted(targets) for node, targets in self._edges.items()},
            "attributes": self._attributes,
        }

