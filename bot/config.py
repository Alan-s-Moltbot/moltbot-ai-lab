from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    request_timeout_seconds: int
    default_provider: str

    ollama_base_url: str
    ollama_model: str

    gemini_api_key: str | None
    gemini_model: str

    azure_foundry_endpoint: str | None
    azure_foundry_api_key: str | None
    azure_foundry_model: str | None
    azure_foundry_api_version: str


VALID_PROVIDERS = {"ollama", "gemini", "azure"}


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def load_settings() -> Settings:
    telegram_bot_token = _env("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    default_provider = (_env("DEFAULT_PROVIDER", "ollama") or "ollama").lower()
    if default_provider not in VALID_PROVIDERS:
        raise RuntimeError(
            f"DEFAULT_PROVIDER must be one of {sorted(VALID_PROVIDERS)}, got: {default_provider}"
        )

    return Settings(
        telegram_bot_token=telegram_bot_token,
        request_timeout_seconds=int(_env("REQUEST_TIMEOUT_SECONDS", "60") or "60"),
        default_provider=default_provider,
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://ollama:11434") or "http://ollama:11434",
        ollama_model=_env("OLLAMA_MODEL", "llama3.1:8b") or "llama3.1:8b",
        gemini_api_key=_env("GEMINI_API_KEY"),
        gemini_model=_env("GEMINI_MODEL", "gemini-1.5-flash") or "gemini-1.5-flash",
        azure_foundry_endpoint=_env("AZURE_FOUNDRY_ENDPOINT"),
        azure_foundry_api_key=_env("AZURE_FOUNDRY_API_KEY"),
        azure_foundry_model=_env("AZURE_FOUNDRY_MODEL"),
        azure_foundry_api_version=(
            _env("AZURE_FOUNDRY_API_VERSION", "2024-05-01-preview")
            or "2024-05-01-preview"
        ),
    )
