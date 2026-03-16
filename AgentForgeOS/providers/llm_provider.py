"""
LLM provider interface for AgentForgeOS.
Concrete implementations (OpenAI via FAL.ai, etc.) should implement this
contract to keep provider-specific logic isolated from services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncIterator


class LLMProvider(ABC):
    """Abstract interface for large language model providers."""

    @abstractmethod
    async def chat(self, prompt: str, **kwargs: Any) -> str:
        """Generate a chat completion for the given prompt."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream tokens for a prompt."""
        raise NotImplementedError

    @abstractmethod
    def model_info(self) -> Dict[str, Optional[str]]:
        """Return metadata about the provider/model."""
        raise NotImplementedError
