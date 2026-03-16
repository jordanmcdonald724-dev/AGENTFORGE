from __future__ import annotations

from typing import Dict, List

from services.pattern_extractor import PatternExtractor


class KnowledgePatternExtractor:
    """Exposes pattern extraction for knowledge ingestion."""

    def __init__(self, extractor: PatternExtractor | None = None) -> None:
        self.extractor = extractor or PatternExtractor()

    def extract(self, text: str) -> Dict[str, List[str]]:
        return self.extractor.extract(text)

