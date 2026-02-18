from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from html import escape

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import requests

from bot.config import Settings, load_settings
from bot.providers import ProviderRouter


logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("moltbot")
MAX_EXEC_OUTPUT_CHARS = 3000


def _is_admin(update: Update, settings: Settings) -> bool:
    user = update.effective_user
    if not user:
        return False
    return user.id in settings.admin_user_ids


async def _require_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    settings: Settings = context.application.bot_data["settings"]
    if _is_admin(update, settings):
        return True
    await update.effective_message.reply_text("Admin access required. Add your Telegram user ID to ADMIN_USER_IDS.")
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi, I'm Moltbot. Send a message and I will route it to an AI backend.\n\n"
        "Optional prefixes:\n"
        "- ollama: <prompt>\n"
        "- gemini: <prompt>\n"
        "- minimax: <prompt>\n"
        "- azure: <prompt>\n\n"
        "Control commands:\n"
        "- /whoami\n"
        "- /adminhelp"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Routing rules:\n"
        "1) Prefix prompt with provider (ollama/gemini/minimax/azure) to force backend.\n"
        "2) Without prefix, DEFAULT_PROVIDER is used.\n"
        "3) If gemini/minimax/azure isn't configured, bot falls back to ollama.\n\n"
        "Use /adminhelp for admin control commands."
    )


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return
    await update.message.reply_text(
        f"user_id={user.id}\nchat_id={chat.id}\nusername={user.username or '(none)'}"
    )


async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update, context):
        return
    await update.message.reply_text(
        "Admin commands:\n"
        "/status - bot + ollama health\n"
        "/models - list Ollama models\n"
        "/pull <model> - pull Ollama model\n"
        "/exec <cmd> - run shell command in bot container (requires ALLOW_UNSAFE_EXEC=true)"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update, context):
        return

    settings: Settings = context.application.bot_data["settings"]
    start_time: datetime = context.application.bot_data["start_time"]
    uptime_seconds = int((datetime.now(timezone.utc) - start_time).total_seconds())
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        response = await asyncio.to_thread(
            requests.get,
            url,
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])
        await update.message.reply_text(
            f"Bot uptime: {uptime_seconds}s\n"
            f"Ollama URL: {settings.ollama_base_url}\n"
            f"Ollama status: OK\n"
            f"Installed models: {len(models)}"
        )
    except Exception as exc:  # noqa: BLE001
        await update.message.reply_text(
            f"Bot uptime: {uptime_seconds}s\n"
            f"Ollama URL: {settings.ollama_base_url}\n"
            f"Ollama status: ERROR ({exc})"
        )


async def models(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update, context):
        return

    settings: Settings = context.application.bot_data["settings"]
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        data = response.json()
        models_data = data.get("models", [])
        if not models_data:
            await update.message.reply_text("No Ollama models installed.")
            return
        lines = [f"- {item.get('name', 'unknown')}" for item in models_data]
        await update.message.reply_text("Installed Ollama models:\n" + "\n".join(lines[:100]))
    except Exception as exc:  # noqa: BLE001
        await update.message.reply_text(f"Failed to list models: {exc}")


async def pull_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update, context):
        return

    settings: Settings = context.application.bot_data["settings"]
    if not context.args:
        await update.message.reply_text("Usage: /pull <model>\nExample: /pull qwen2.5:7b")
        return
    model = context.args[0].strip()
    if not model:
        await update.message.reply_text("Model cannot be empty.")
        return

    await update.message.reply_text(f"Pulling model `{model}` ... this may take a while.", parse_mode="Markdown")
    url = f"{settings.ollama_base_url.rstrip('/')}/api/pull"
    payload = {"name": model, "stream": False}
    try:
        response = await asyncio.to_thread(
            requests.post,
            url,
            json=payload,
            timeout=max(settings.request_timeout_seconds, 600),
        )
        response.raise_for_status()
        await update.message.reply_text(f"Model pull completed: {model}")
    except Exception as exc:  # noqa: BLE001
        await update.message.reply_text(f"Failed to pull model {model}: {exc}")


async def exec_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update, context):
        return

    settings: Settings = context.application.bot_data["settings"]
    if not settings.allow_unsafe_exec:
        await update.message.reply_text("Command execution is disabled. Set ALLOW_UNSAFE_EXEC=true to enable /exec.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /exec <shell command>")
        return

    command = " ".join(context.args).strip()
    if not command:
        await update.message.reply_text("Command cannot be empty.")
        return

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    combined = (stdout + stderr).decode(errors="replace")
    if not combined:
        combined = "(no output)"
    if len(combined) > MAX_EXEC_OUTPUT_CHARS:
        combined = combined[:MAX_EXEC_OUTPUT_CHARS] + "\n...[truncated]"
    await update.message.reply_text(
        f"exit={process.returncode}\n<pre>{escape(combined)}</pre>",
        parse_mode="HTML",
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    router: ProviderRouter = context.application.bot_data["router"]

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        result = router.ask(update.message.text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to process prompt")
        await update.message.reply_text(f"Error while processing your request: {exc}")
        return

    header = f"Provider: {result.provider}"
    if result.warning:
        header = f"{header}\nWarning: {result.warning}"

    await update.message.reply_text(f"{header}\n\n{result.response_text}")


def main() -> None:
    load_dotenv()
    settings = load_settings()
    router = ProviderRouter(settings)

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.bot_data["router"] = router
    application.bot_data["settings"] = settings
    application.bot_data["start_time"] = datetime.now(timezone.utc)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("whoami", whoami))
    application.add_handler(CommandHandler("adminhelp", admin_help))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("models", models))
    application.add_handler(CommandHandler("pull", pull_model))
    application.add_handler(CommandHandler("exec", exec_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Starting Moltbot polling loop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
