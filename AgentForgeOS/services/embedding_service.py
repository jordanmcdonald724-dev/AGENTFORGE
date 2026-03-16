"""
Embedding Service
=================
Wraps provider embeddings for use with the vector store.
"""

from typing import List
import numpy as np
from providers.llm_provider import LLMProvider


class EmbeddingService:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def embed(self, texts: List[str]) -> List[np.ndarray]:
        # Placeholder: deterministic hash-based embedding for bootstrap
        vectors = []
        for text in texts:
            seed = sum(ord(c) for c in text)
            np.random.seed(seed % (2**32 - 1))
            vectors.append(np.random.rand(384))
        return vectors
