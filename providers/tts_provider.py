from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class TTSProvider(ABC):
    """Interface for text-to-speech providers."""

    @abstractmethod
    async def speak(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Convert text to speech and return provider-specific metadata."""
        raise NotImplementedError

