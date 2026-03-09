"""Anthropic Claude LLM Adapter."""
import os
from llm import BaseLLM


class ClaudeAdapter(BaseLLM):
    def __init__(self, api_key=None, model="claude-sonnet-4-20250514"):
        try:
            import anthropic
        except ImportError:
            raise ImportError("pip install anthropic")
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def chat(self, messages, **kwargs):
        # Extract system message if present
        system = ""
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                chat_messages.append(m)

        response = self.client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=chat_messages,
        )
        return response.content[0].text

    def stream(self, messages, **kwargs):
        system = ""
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                chat_messages.append(m)

        with self.client.messages.stream(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=chat_messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
