"""
Image provider interface for AgentForgeOS.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ImageProvider(ABC):
    """Abstract interface for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate an image and return metadata (e.g., URL, dimensions)."""
        raise NotImplementedError
