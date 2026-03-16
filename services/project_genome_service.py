from __future__ import annotations

from typing import Dict, List

from .knowledge_graph import KnowledgeGraphService
from .pattern_extractor import PatternExtractor


class ProjectGenomeService:
    """Aggregates knowledge about a project into a concise genome."""

    def __init__(self, graph: KnowledgeGraphService, patterns: PatternExtractor) -> None:
        self.graph = graph
        self.patterns = patterns

    def compile_genome(self, project_id: str, documents: List[str]) -> Dict[str, object]:
        headings = []
        signals = []
        for doc in documents:
            extracted = self.patterns.extract(doc)
            headings.extend(extracted["headings"])
            signals.extend(extracted["signals"])
        self.graph.add_attributes(project_id, {"signals": ",".join(sorted(set(signals)))})
        return {
            "project_id": project_id,
            "headings": sorted(set(headings)),
            "signals": sorted(set(signals)),
            "graph": self.graph.snapshot(),
        }

