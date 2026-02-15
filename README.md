# Moltbot AI Lab

This repository now contains a **Moltbot Telegram agent** designed to run in Docker and route AI requests to:

1. **Local Ollama** (default)
2. **Gemini** (optional)
3. **Azure AI Foundry** (optional)

## What this project includes

- Telegram bot service (`bot/main.py`) built with `python-telegram-bot`
- Provider routing logic with conditional backend selection (`bot/providers.py`)
- Environment-based configuration (`bot/config.py`)
- Custom Docker image with required runtime libraries (`Dockerfile`)
- Compose stack for bot + Ollama (`docker-compose.yml`)

## Provider routing behavior

By default, all messages go to Ollama.

You can override provider per message by prefixing the prompt:

- `gemini: <your prompt>`
- `azure: <your prompt>`
- `ollama: <your prompt>`

If a requested provider is not configured, the bot falls back to Ollama and explains why.

## Environment variables

Copy `.env.example` to `.env` and fill values:

```bash
cp .env.example .env
```

Required:

- `TELEGRAM_BOT_TOKEN`

Optional (for local Ollama):

- `OLLAMA_BASE_URL` (default `http://ollama:11434` in Docker)
- `OLLAMA_MODEL` (default `llama3.1:8b`)

Optional (Gemini):

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (default `gemini-1.5-flash`)

Optional (Azure AI Foundry):

- `AZURE_FOUNDRY_ENDPOINT`
- `AZURE_FOUNDRY_API_KEY`
- `AZURE_FOUNDRY_MODEL`
- `AZURE_FOUNDRY_API_VERSION` (default `2024-05-01-preview`)

Optional global behavior:

- `DEFAULT_PROVIDER` (`ollama`, `gemini`, or `azure`; default `ollama`)
- `REQUEST_TIMEOUT_SECONDS` (default `60`)

## Run with Docker Compose

```bash
docker compose up --build -d
```

Then pull an Ollama model in the Ollama container once:

```bash
docker compose exec ollama ollama pull llama3.1:8b
```

Tail logs:

```bash
docker compose logs -f bot
```

## Run locally (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

## Notes

- The bot uses long polling, so no webhook setup is required.
- Keep API keys in `.env` only (do not commit secrets).
