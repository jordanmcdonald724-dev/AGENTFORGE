"""
Knowledge Graph Service
=======================
Minimal stub for capturing entities/relationships.
"""

from typing import Dict, Set, Tuple


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Set[Tuple[str, str, str]] = set()

    def add_fact(self, subject: str, relation: str, obj: str) -> None:
        self.nodes.update([subject, obj])
        self.edges.add((subject, relation, obj))

    def neighbors(self, subject: str):
        return [(s, r, o) for (s, r, o) in self.edges if s == subject]
