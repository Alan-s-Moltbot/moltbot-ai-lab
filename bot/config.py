from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    request_timeout_seconds: int
    admin_user_ids: tuple[int, ...]
    allow_unsafe_exec: bool

    minimax_api_key: str
    minimax_base_url: str
    minimax_model: str


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

    minimax_api_key = _env("MINIMAX_API_KEY")
    if not minimax_api_key:
        raise RuntimeError("MINIMAX_API_KEY is required")

    return Settings(
        telegram_bot_token=telegram_bot_token,
        request_timeout_seconds=int(_env("REQUEST_TIMEOUT_SECONDS", "60") or "60"),
        admin_user_ids=_parse_admin_ids(_env("ADMIN_USER_IDS")),
        allow_unsafe_exec=_parse_bool(_env("ALLOW_UNSAFE_EXEC"), default=False),
        minimax_api_key=minimax_api_key,
        minimax_base_url=_env("MINIMAX_BASE_URL", "https://api.minimax.io") or "https://api.minimax.io",
        minimax_model=_env("MINIMAX_MODEL", "MiniMax-M2.5") or "MiniMax-M2.5",
    )
