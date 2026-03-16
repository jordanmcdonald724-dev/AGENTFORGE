from __future__ import annotations

import hashlib
from typing import Iterable, List


class EmbeddingService:
    """Minimal, provider-agnostic embedding generator for internal usage."""

    def embed(self, text: str) -> List[float]:
        # Deterministic hash-based embedding to avoid external dependencies.
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # Produce a small vector while keeping it reproducible.
        return [int.from_bytes(digest[i : i + 4], "big") / 1_000_000 for i in range(0, 32, 4)]

    def embed_corpus(self, texts: Iterable[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]

