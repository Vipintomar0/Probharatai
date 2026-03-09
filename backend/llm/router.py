"""LLM Router - dynamically selects the right LLM adapter based on config."""
import logging
from config import DEFAULT_LLM_PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, OLLAMA_BASE_URL, OPENROUTER_API_KEY
from database.models import get_api_key

logger = logging.getLogger("probharatai.llm")

# Adapter registry
_ADAPTERS = {}


def get_adapter(provider=None, **kwargs):
    """Get or create an LLM adapter for the given provider."""
    provider = provider or DEFAULT_LLM_PROVIDER
    provider = provider.lower().strip()

    cache_key = f"{provider}_{kwargs.get('model', 'default')}"
    if cache_key in _ADAPTERS:
        return _ADAPTERS[cache_key]

    # Try to get API key from database first, then env
    db_key = get_api_key(provider)

    if provider == "openai":
        from llm.openai_adapter import OpenAIAdapter
        adapter = OpenAIAdapter(api_key=db_key or OPENAI_API_KEY, **kwargs)

    elif provider in ("claude", "anthropic"):
        from llm.claude import ClaudeAdapter
        adapter = ClaudeAdapter(api_key=db_key or ANTHROPIC_API_KEY, **kwargs)

    elif provider == "groq":
        from llm.groq_adapter import GroqAdapter
        adapter = GroqAdapter(api_key=db_key or GROQ_API_KEY, **kwargs)

    elif provider == "gemini":
        from llm.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key=db_key or GEMINI_API_KEY, **kwargs)

    elif provider == "ollama":
        from llm.ollama import OllamaAdapter
        adapter = OllamaAdapter(base_url=OLLAMA_BASE_URL, **kwargs)

    elif provider == "openrouter":
        from llm.openai_adapter import OpenAIAdapter
        # OpenRouter is OpenAI-compatible
        adapter = OpenAIAdapter(api_key=db_key or OPENROUTER_API_KEY, **kwargs)
        adapter.client.base_url = "https://openrouter.ai/api/v1"

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    _ADAPTERS[cache_key] = adapter
    logger.info(f"Initialized LLM adapter: {provider}")
    return adapter


def chat(messages, provider=None, **kwargs):
    """Convenience: single call to chat with any provider."""
    adapter = get_adapter(provider, **kwargs)
    return adapter.chat(messages, **kwargs)


def stream(messages, provider=None, **kwargs):
    """Convenience: stream responses from any provider."""
    adapter = get_adapter(provider, **kwargs)
    return adapter.stream(messages, **kwargs)
