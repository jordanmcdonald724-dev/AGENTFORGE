from __future__ import annotations

from typing import Iterable, List

from services.embedding_service import EmbeddingService


class KnowledgeEmbeddingService:
    """Embedding utility dedicated to the knowledge layer."""

    def __init__(self, base: EmbeddingService | None = None) -> None:
        self.base = base or EmbeddingService()

    def embed(self, text: str) -> List[float]:
        return self.base.embed(text)

    def embed_corpus(self, texts: Iterable[str]) -> List[List[float]]:
        return self.base.embed_corpus(texts)

