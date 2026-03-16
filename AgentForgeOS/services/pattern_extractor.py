"""
Pattern Extractor
=================
Extracts reusable patterns from project artifacts.
"""

from typing import List


class PatternExtractor:
    def extract(self, texts: List[str]) -> List[str]:
        return list({text.strip() for text in texts if text.strip()})
