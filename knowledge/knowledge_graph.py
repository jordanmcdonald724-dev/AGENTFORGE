from __future__ import annotations

from typing import Dict, List

from services.knowledge_graph import KnowledgeGraphService


class KnowledgeGraph:
    """Persistent knowledge graph tailored for agent discovery."""

    def __init__(self, service: KnowledgeGraphService | None = None) -> None:
        self.service = service or KnowledgeGraphService()

    def link(self, source: str, target: str) -> None:
        self.service.add_edge(source, target)

    def describe(self, node: str) -> Dict[str, object]:
        return {
            "neighbors": self.service.neighbors(node),
            "attributes": self.service.describe(node),
        }

    def snapshot(self) -> Dict[str, object]:
        return self.service.snapshot()

