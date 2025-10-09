from __future__ import annotations

import os
from typing import List

import google.generativeai as genai

from .base import BaseProvider
from ..data_model import ConversationTurn


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set in the environment.")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        genai.configure(api_key=self.api_key)
        self._client = genai.GenerativeModel(self.model_name)

    def _build_history(self, history: List[ConversationTurn] | None) -> list[dict]:
        turns: list[dict] = []
        if not history:
            return turns
        for turn in history:
            role = "user" if turn.speaker == "user" else "model"
            turns.append({"role": role, "parts": [turn.text]})
        return turns

    def generate(self, prompt: str, history: list[ConversationTurn] | None = None) -> str:
        try:
            # Start a chat session with prior turns when provided
            if history:
                chat = self._client.start_chat(history=self._build_history(history))
                resp = chat.send_message(prompt)
            else:
                resp = self._client.generate_content(prompt)
            # Extract text safely
            text = getattr(resp, "text", None)
            if not text and hasattr(resp, "candidates") and resp.candidates:
                parts = getattr(resp.candidates[0], "content", None)
                if parts and getattr(parts, "parts", None):
                    text = "".join(p.text for p in parts.parts if getattr(p, "text", None))
            return text or "Tell me more."
        except Exception as e:
            return f"Error calling Gemini API: {e}"


