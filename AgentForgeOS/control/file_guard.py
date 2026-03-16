"""
File Guard
==========
Enforces repository editing permissions to prevent uncontrolled changes to
protected system layers.
"""

from pathlib import Path
from typing import Iterable

PROTECTED_DIRECTORIES = {"engine", "services", "providers", "control"}


def is_protected(path: Path) -> bool:
    """Return True if the path resides in a protected directory."""
    parts = path.parts
    return any(part in PROTECTED_DIRECTORIES for part in parts)


def assert_write_allowed(paths: Iterable[Path]) -> None:
    """Raise PermissionError if any path is protected."""
    for path in paths:
        if is_protected(path):
            raise PermissionError(f"Write denied for protected path: {path}")
