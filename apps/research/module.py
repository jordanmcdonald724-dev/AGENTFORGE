from __future__ import annotations

from typing import Dict, List, Tuple

from knowledge.embedding_service import KnowledgeEmbeddingService
from knowledge.vector_store import KnowledgeVectorStore


class ResearchApp:
    """Provides lightweight research capabilities backed by the knowledge system."""

    def __init__(self, embeddings: KnowledgeEmbeddingService, store: KnowledgeVectorStore) -> None:
        self.embeddings = embeddings
        self.store = store

    def index(self, documents: List[str]) -> int:
        for doc in documents:
            self.store.add(self.embeddings.embed(doc), {"document": doc})
        return len(documents)

    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict[str, str]]]:
        return self.store.search(self.embeddings.embed(query), top_k=top_k)

