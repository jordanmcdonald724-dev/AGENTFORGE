"""
Bridge Security
===============
Applies basic checks for bridge operations.
"""

from pathlib import Path


def validate_path(path: Path) -> bool:
    # Minimal path validation placeholder
    return not path.is_absolute()
