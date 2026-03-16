from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """Interface for language model providers."""

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Execute a chat completion request and return the response text."""
        raise NotImplementedError

