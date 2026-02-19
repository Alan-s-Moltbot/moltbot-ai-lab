from __future__ import annotations

from dataclasses import dataclass

import requests

from bot.config import Settings


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    prompt: str
    response_text: str


class ProviderRouter:
    def __init__(self, settings: Settings):
        self.settings = settings

    def ask(self, message_text: str) -> ProviderResult:
        prompt = message_text.strip()
        if not prompt:
            return ProviderResult(provider="minimax", prompt=prompt, response_text="Please send a non-empty prompt.")

        return ProviderResult(provider="minimax", prompt=prompt, response_text=self._ask_minimax(prompt))

    def _ask_minimax(self, prompt: str) -> str:
        base_url = self.settings.minimax_base_url.rstrip("/")
        url = f"{base_url}/v1/text/chatcompletion_v2"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.minimax_api_key}",
        }
        payload = {
            "model": self.settings.minimax_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "stream": False,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=self.settings.request_timeout_seconds)
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])
        if not choices:
            return "(No response from MiniMax)"

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content.strip() or "(No response from MiniMax)"

        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            joined = "\n".join(chunk for chunk in chunks if chunk)
            return joined.strip() or "(No response from MiniMax)"

        return "(No response from MiniMax)"
