"""OpenAI LLM Adapter."""
import os
from llm import BaseLLM


class OpenAIAdapter(BaseLLM):
    def __init__(self, api_key=None, model="gpt-4o"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("pip install openai")
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
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
