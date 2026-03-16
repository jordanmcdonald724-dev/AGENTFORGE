from __future__ import annotations

from typing import Dict

from services.vector_store import VectorStore


class DeploymentApp:
    """Manages deployment metadata without coupling to engine internals."""

    def __init__(self, store: VectorStore) -> None:
        self.store = store

    def plan(self, project_id: str, target: str) -> Dict[str, str]:
        self.store.add([1.0], {"project_id": project_id, "target": target})
        return {"project_id": project_id, "target": target, "status": "planned"}

