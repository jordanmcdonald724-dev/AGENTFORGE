from __future__ import annotations

from typing import Dict, List

from .pattern_extractor import PatternExtractor


class AutopsyService:
    """Post-run analysis to identify stability and governance issues."""

    def __init__(self, extractor: PatternExtractor) -> None:
        self.extractor = extractor

    def analyze_run(self, logs: List[str]) -> Dict[str, object]:
        findings = [self.extractor.extract(log) for log in logs]
        all_signals = sorted({signal for f in findings for signal in f["signals"]})
        return {
            "events_processed": len(logs),
            "signals": all_signals,
            "action_required": bool(all_signals),
        }

