"""LLM Adapter Base & Router - supports OpenAI, Claude, Groq, Gemini, Ollama, OpenRouter."""
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract base class for all LLM adapters."""

    @abstractmethod
    def chat(self, messages: list, **kwargs) -> str:
        """Send messages and return the assistant's response text."""
        pass

    @abstractmethod
    def stream(self, messages: list, **kwargs):
        """Stream responses token by token."""
        pass
