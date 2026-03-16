from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class VectorRecord:
    vector: List[float]
    metadata: Dict[str, Any]


class VectorStore:
    """In-memory vector store with lightweight similarity search."""

    def __init__(self) -> None:
        self._records: List[VectorRecord] = []

    def add(self, vector: List[float], metadata: Dict[str, Any]) -> None:
        self._records.append(VectorRecord(vector=vector, metadata=metadata))

    def search(self, query: List[float], top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        scored = [( _cosine_similarity(query, record.vector), record.metadata) for record in self._records]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[:top_k]

    def clear(self) -> None:
        self._records.clear()

