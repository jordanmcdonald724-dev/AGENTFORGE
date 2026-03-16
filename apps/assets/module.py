from __future__ import annotations

from typing import Dict, List


class AssetsApp:
    """Tracks asset pipeline state and metadata."""

    def __init__(self) -> None:
        self.assets: List[Dict[str, str]] = []

    def register(self, asset_id: str, kind: str, location: str) -> Dict[str, str]:
        record = {"asset_id": asset_id, "kind": kind, "location": location}
        self.assets.append(record)
        return record

