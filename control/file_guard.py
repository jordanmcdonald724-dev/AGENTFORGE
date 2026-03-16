from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Set

import yaml

PERMISSION_MATRIX_PATH = Path(__file__).resolve().parent / "permission_matrix.yaml"
logger = logging.getLogger(__name__)


class FileGuard:
    """Prevents writes to protected directories using a permission matrix."""

    def __init__(self, protected: Iterable[str] | None = None) -> None:
        self._matrix = self._load_matrix()
        self.protected: Set[Path] = {Path(p).resolve() for p in (protected or self._matrix.get("protected_directories", []))}

    def _load_matrix(self) -> dict:
        if PERMISSION_MATRIX_PATH.exists():
            return yaml.safe_load(PERMISSION_MATRIX_PATH.read_text()) or {}
        return {"protected_directories": []}

    def is_allowed(self, target: str) -> bool:
        path = Path(target).resolve()
        return not any(str(path).startswith(str(protected)) for protected in self.protected)

    def ensure_allowed(self, target: str) -> None:
        if not self.is_allowed(target):
            logger.warning("Access denied to %s", target)
            raise PermissionError(f"Write operations are blocked for {target}")

