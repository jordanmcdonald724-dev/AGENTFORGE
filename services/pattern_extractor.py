from __future__ import annotations

import re
from typing import Dict, List


class PatternExtractor:
    """Extract recurring patterns or signals from plain text."""

    CODE_PATTERN = re.compile(r"(TODO|FIXME|BUG)", re.IGNORECASE)

    def extract(self, text: str) -> Dict[str, List[str]]:
        tags = [match.group(1).upper() for match in self.CODE_PATTERN.finditer(text)]
        headings = re.findall(r"^#+\s+(.+)$", text, flags=re.MULTILINE)
        return {"signals": tags, "headings": headings}
