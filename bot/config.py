from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    request_timeout_seconds: int
    default_provider: str
    admin_user_ids: tuple[int, ...]
    allow_unsafe_exec: bool

    ollama_base_url: str
    ollama_model: str

    gemini_api_key: str | None
    gemini_model: str

    minimax_api_key: str | None
    minimax_base_url: str
    minimax_model: str

    azure_foundry_endpoint: str | None
    azure_foundry_api_key: str | None
    azure_foundry_model: str | None
    azure_foundry_api_version: str


VALID_PROVIDERS = {"ollama", "gemini", "minimax", "azure"}


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _parse_admin_ids(value: str | None) -> tuple[int, ...]:
    if not value:
        return ()
    ids: list[int] = []
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        try:
            ids.append(int(item))
        except ValueError as exc:
            raise RuntimeError(f"Invalid ADMIN_USER_IDS entry: {item}") from exc
    return tuple(ids)


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
        admin_user_ids=_parse_admin_ids(_env("ADMIN_USER_IDS")),
        allow_unsafe_exec=_parse_bool(_env("ALLOW_UNSAFE_EXEC"), default=False),
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://ollama:11434") or "http://ollama:11434",
        ollama_model=_env("OLLAMA_MODEL", "llama3.1:8b") or "llama3.1:8b",
        gemini_api_key=_env("GEMINI_API_KEY"),
        gemini_model=_env("GEMINI_MODEL", "gemini-1.5-flash") or "gemini-1.5-flash",
        minimax_api_key=_env("MINIMAX_API_KEY"),
        minimax_base_url=_env("MINIMAX_BASE_URL", "https://api.minimax.io") or "https://api.minimax.io",
        minimax_model=_env("MINIMAX_MODEL", "MiniMax-M2.5") or "MiniMax-M2.5",
        azure_foundry_endpoint=_env("AZURE_FOUNDRY_ENDPOINT"),
        azure_foundry_api_key=_env("AZURE_FOUNDRY_API_KEY"),
        azure_foundry_model=_env("AZURE_FOUNDRY_MODEL"),
        azure_foundry_api_version=(
            _env("AZURE_FOUNDRY_API_VERSION", "2024-05-01-preview")
            or "2024-05-01-preview"
        ),
    )
