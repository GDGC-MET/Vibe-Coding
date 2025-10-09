from __future__ import annotations

import os
from typing import List

import requests

from .base import BaseProvider
from ..data_model import ConversationTurn


class PerplexityProvider(BaseProvider):
    name = "perplexity"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 20) -> None:
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.model = model or os.getenv("PERPLEXITY_MODEL", "llama-3.1-mini")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY is not set in the environment.")

    def _build_messages(self, prompt: str, history: List[ConversationTurn] | None) -> list[dict]:
        messages: list[dict] = []
        if history:
            for turn in history:
                role = "user" if turn.speaker == "user" else "assistant"
                messages.append({"role": role, "content": turn.text})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, history: list[ConversationTurn] | None = None) -> str:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": self._build_messages(prompt, history),
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code >= 400:
                # Surface a concise server message; users can adjust PERPLEXITY_MODEL per docs
                txt = resp.text
                if len(txt) > 200:
                    txt = txt[:200] + "..."
                return f"Perplexity error {resp.status_code}: {txt}"
            data = resp.json()
            # Try common shapes in order of likelihood
            # 1) OpenAI-style chat response
            content = None
            try:
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content")
                )
            except Exception:
                content = None
            # 2) Some servers return a top-level 'output_text'
            if not content:
                content = data.get("output_text")
            # 3) Fallback: first choice text
            if not content:
                content = (
                    data.get("choices", [{}])[0].get("text")
                )
            return content or "Tell me more."
        except requests.RequestException as e:
            return f"Network error talking to Perplexity: {e}"

import os
import requests
from typing import List
from ..data_model import ConversationTurn
from .base import BaseProvider

class PerplexityProvider(BaseProvider):
    name = "perplexity"

    def __init__(self, api_key: str | None = None, model: str = "lllama-3-sonar-small-32k-online") -> None:
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key not provided. Set the PERPLEXITY_API_KEY environment variable.")
        # Allow model override via env var
        self.model = os.getenv("PERPLEXITY_MODEL", model)
        self.api_url = os.getenv("PERPLEXITY_API_URL", "https://api.perplexity.ai/chat/completions")

    def generate(self, prompt: str, history: list[ConversationTurn]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        messages = [{"role": "system", "content": "You are an AI assistant."}]
        for turn in history:
            messages.append({"role": "user" if turn.speaker == "user" else "assistant", "content": turn.text})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            # If an error occurs, include server-provided details to aid debugging
            if not response.ok:
                try:
                    err_json = response.json()
                    # OpenAI-compatible error format
                    if isinstance(err_json, dict) and "error" in err_json:
                        detail = err_json["error"].get("message") or err_json["error"]
                    else:
                        detail = err_json
                except Exception:
                    detail = response.text
                return f"Error calling Perplexity API: {response.status_code} {response.reason}: {detail}"

            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Error calling Perplexity API: {e}"
