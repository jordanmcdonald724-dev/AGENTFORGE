"""
Text-to-speech provider interface for AgentForgeOS.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class TTSProvider(ABC):
    """Abstract interface for text-to-speech providers."""

    @abstractmethod
    async def speak(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Synthesize speech from text and return audio metadata/bytes."""
        raise NotImplementedError
