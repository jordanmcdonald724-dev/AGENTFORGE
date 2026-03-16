from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ImageProvider(ABC):
    """Interface for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate an image and return provider-specific metadata."""
        raise NotImplementedError

