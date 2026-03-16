"""
Vector Store Service
====================
Lightweight in-memory vector store for bootstrap purposes.
"""

from typing import List, Tuple
import numpy as np


class VectorStore:
    def __init__(self):
        self._vectors: List[Tuple[str, np.ndarray]] = []

    def add(self, key: str, vector: np.ndarray) -> None:
        self._vectors.append((key, vector))

    def search(self, query: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        scores = [
            (key, float(np.dot(vec, query) / (np.linalg.norm(vec) * np.linalg.norm(query) + 1e-9)))
            for key, vec in self._vectors
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
