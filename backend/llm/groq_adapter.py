"""Groq LLM Adapter."""
import os
from llm import BaseLLM


class GroqAdapter(BaseLLM):
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("pip install groq")
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = model

    def chat(self, messages, **kwargs):
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        return response.choices[0].message.content

    def stream(self, messages, **kwargs):
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
