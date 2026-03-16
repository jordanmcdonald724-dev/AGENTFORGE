from __future__ import annotations

import secrets
from typing import Optional


class BridgeSecurity:
    """Minimal shared-secret verifier for bridge operations."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or secrets.token_hex(8)

    def assert_token(self, presented: Optional[str]) -> None:
        if not presented or not secrets.compare_digest(str(presented), str(self.token)):
            raise PermissionError("Bridge token rejected")

