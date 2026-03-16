from __future__ import annotations

from typing import Any, Dict, List, Tuple

from services.vector_store import VectorStore


class KnowledgeVectorStore:
    """Vector store dedicated to long-term knowledge retention."""

    def __init__(self, store: VectorStore | None = None) -> None:
        self.store = store or VectorStore()

    def add(self, vector: List[float], metadata: Dict[str, Any]) -> None:
        self.store.add(vector, metadata)

    def search(self, query: List[float], top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        return self.store.search(query, top_k)

    def clear(self) -> None:
        self.store.clear()

