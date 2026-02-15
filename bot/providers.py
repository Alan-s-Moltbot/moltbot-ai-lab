from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import requests

from bot.config import Settings


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    prompt: str
    response_text: str
    warning: str | None = None


class ProviderRouter:
    def __init__(self, settings: Settings):
        self.settings = settings

    def resolve_provider_and_prompt(self, text: str) -> Tuple[str, str]:
        raw = text.strip()
        lowered = raw.lower()

        for provider in ("ollama", "gemini", "azure"):
            prefix = f"{provider}:"
            if lowered.startswith(prefix):
                return provider, raw[len(prefix) :].strip()

        return self.settings.default_provider, raw

    def ask(self, message_text: str) -> ProviderResult:
        provider, prompt = self.resolve_provider_and_prompt(message_text)
        if not prompt:
            return ProviderResult(provider=provider, prompt=prompt, response_text="Please send a non-empty prompt.")

        if provider == "gemini":
            if not self.settings.gemini_api_key:
                fallback = self._ask_ollama(prompt)
                return ProviderResult(
                    provider="ollama",
                    prompt=prompt,
                    response_text=fallback,
                    warning="Gemini is not configured; fell back to Ollama.",
                )
            return ProviderResult(provider="gemini", prompt=prompt, response_text=self._ask_gemini(prompt))

        if provider == "azure":
            if not (
                self.settings.azure_foundry_endpoint
                and self.settings.azure_foundry_api_key
                and self.settings.azure_foundry_model
            ):
                fallback = self._ask_ollama(prompt)
                return ProviderResult(
                    provider="ollama",
                    prompt=prompt,
                    response_text=fallback,
                    warning="Azure AI Foundry is not configured; fell back to Ollama.",
                )
            return ProviderResult(provider="azure", prompt=prompt, response_text=self._ask_azure(prompt))

        return ProviderResult(provider="ollama", prompt=prompt, response_text=self._ask_ollama(prompt))

    def _ask_ollama(self, prompt: str) -> str:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        response = requests.post(url, json=payload, timeout=self.settings.request_timeout_seconds)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "(No response from Ollama)").strip()

    def _ask_gemini(self, prompt: str) -> str:
        model = self.settings.gemini_model
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.settings.gemini_api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=self.settings.request_timeout_seconds)
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return "(No response from Gemini)"

        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
        return "\n".join(tp for tp in text_parts if tp).strip() or "(No response from Gemini)"

    def _ask_azure(self, prompt: str) -> str:
        endpoint = self.settings.azure_foundry_endpoint.rstrip("/")
        model = self.settings.azure_foundry_model
        api_version = self.settings.azure_foundry_api_version

        if "api-version=" in endpoint:
            url = endpoint
        else:
            separator = "&" if "?" in endpoint else "?"
            url = f"{endpoint}{separator}api-version={api_version}"

        headers = {
            "Content-Type": "application/json",
            "api-key": self.settings.azure_foundry_api_key or "",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=self.settings.request_timeout_seconds)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return "(No response from Azure AI Foundry)"

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content.strip() or "(No response from Azure AI Foundry)"

        if isinstance(content, list):
            chunks = [c.get("text", "") for c in content if isinstance(c, dict)]
            joined = "\n".join(chunk for chunk in chunks if chunk)
            return joined.strip() or "(No response from Azure AI Foundry)"

        return "(No response from Azure AI Foundry)"
