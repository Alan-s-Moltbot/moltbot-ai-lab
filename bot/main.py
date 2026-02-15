from __future__ import annotations

import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from bot.config import load_settings
from bot.providers import ProviderRouter


logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("moltbot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi, I'm Moltbot. Send a message and I will route it to an AI backend.\n\n"
        "Optional prefixes:\n"
        "- ollama: <prompt>\n"
        "- gemini: <prompt>\n"
        "- azure: <prompt>"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Routing rules:\n"
        "1) Prefix prompt with provider (ollama/gemini/azure) to force backend.\n"
        "2) Without prefix, DEFAULT_PROVIDER is used.\n"
        "3) If gemini/azure isn't configured, bot falls back to ollama."
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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Starting Moltbot polling loop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
