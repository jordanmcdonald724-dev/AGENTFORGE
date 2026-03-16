"""
Autopsy Service
===============
Records post-mortem insights from failed builds.
"""

from typing import Dict, Any, List


class AutopsyService:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def log_failure(self, project_id: str, details: Dict[str, Any]) -> None:
        self.records.append({"project_id": project_id, **details})

    def list_failures(self) -> List[Dict[str, Any]]:
        return list(self.records)
