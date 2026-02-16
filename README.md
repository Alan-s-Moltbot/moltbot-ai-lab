# Moltbot AI Lab

## OpenClaw-Native Telegram Control (Recommended)

If your goal is to control your agent through Telegram, use OpenClaw directly as the gateway/channel runtime instead of this custom router bot.

### 1) Stop this stack first

```bash
docker compose down
```

### 2) Install OpenClaw

```bash
npm install -g openclaw@latest
```

### 3) Run onboarding

```bash
openclaw onboard
```

During onboarding, enable the Telegram channel and provide your BotFather token.

### 4) Start the OpenClaw gateway

```bash
openclaw gateway
```

### 5) Pair and approve Telegram DM access

Default Telegram DM policy is pairing. Approve pending code(s):

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

### 6) Optional config file path

OpenClaw reads config from:

```text
~/.openclaw/openclaw.json
```

You can also set:

- `TELEGRAM_BOT_TOKEN` as env var, or
- `channels.telegram.botToken` in OpenClaw config (config value takes precedence).

Reference docs:

- https://openclaw.im/docs/channels/telegram
- https://openclaw.im/docs/start/wizard
- https://openclaw.im/docs/gateway/configuration

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
- `ADMIN_USER_IDS` (comma-separated Telegram user IDs that can run admin commands)
- `ALLOW_UNSAFE_EXEC` (`true` to enable `/exec`; default `false`)

## Telegram control commands

Admin commands are available only to users listed in `ADMIN_USER_IDS`.

- `/whoami` shows your Telegram `user_id` and `chat_id`
- `/status` shows bot uptime and Ollama connectivity
- `/models` lists installed Ollama models
- `/pull <model>` pulls an Ollama model from Telegram
- `/exec <cmd>` runs a shell command in the bot container (requires `ALLOW_UNSAFE_EXEC=true`)

Example:

```env
ADMIN_USER_IDS=123456789
ALLOW_UNSAFE_EXEC=false
```

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

## Run locally on Windows (with Ollama already installed)

If Ollama is already running on your Windows host, the fastest setup is to run only the Telegram bot locally.

1. Open PowerShell in this repository.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Copy env template and set required values:

```powershell
copy .env.example .env
```

At minimum, provide:

- `TELEGRAM_BOT_TOKEN` (from BotFather)
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `OLLAMA_MODEL` (example: `llama3.1:8b`)

Optional but useful if Ollama was installed with CORS restrictions:

- In Ollama environment: `OLLAMA_ORIGINS=*` (or a specific origin)

5. Ensure your model is pulled:

```powershell
ollama pull llama3.1:8b
```

6. Start the bot:

```powershell
python -m bot.main
```

If you only want Ollama (no Gemini/Azure), leave Gemini/Azure variables empty.

## Notes

- The bot uses long polling, so no webhook setup is required.
- Keep API keys in `.env` only (do not commit secrets).
