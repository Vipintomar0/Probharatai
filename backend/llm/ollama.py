"""Ollama Local LLM Adapter - zero API cost."""
import os
import json
import requests
from llm import BaseLLM


class OllamaAdapter(BaseLLM):
    def __init__(self, base_url=None, model="llama3.2"):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model

    def chat(self, messages, **kwargs):
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def stream(self, messages, **kwargs):
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                },
            },
            stream=True,
            timeout=120,
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]
