"""Google Gemini LLM Adapter."""
import os
from llm import BaseLLM


class GeminiAdapter(BaseLLM):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("pip install google-generativeai")
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model_name = model
        self.genai = genai

    def _convert_messages(self, messages):
        """Convert OpenAI-style messages to Gemini format."""
        history = []
        system_instruction = None
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})
        return history, system_instruction

    def chat(self, messages, **kwargs):
        history, system_instruction = self._convert_messages(messages)
        model = self.genai.GenerativeModel(
            kwargs.get("model", self.model_name),
            system_instruction=system_instruction,
        )
        chat = model.start_chat(history=history[:-1])
        last_msg = history[-1]["parts"][0] if history else ""
        response = chat.send_message(last_msg)
        return response.text

    def stream(self, messages, **kwargs):
        history, system_instruction = self._convert_messages(messages)
        model = self.genai.GenerativeModel(
            kwargs.get("model", self.model_name),
            system_instruction=system_instruction,
        )
        chat = model.start_chat(history=history[:-1])
        last_msg = history[-1]["parts"][0] if history else ""
        response = chat.send_message(last_msg, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
