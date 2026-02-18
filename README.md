# Moltbot AI Lab

This repository is now configured for **OpenClaw inside Docker** with Telegram control and local Ollama.

## Architecture

- `openclaw` service: runs `openclaw gateway`
- `ollama` service: serves local models
- `openclaw_data` volume: persists OpenClaw onboarding/config
- `ollama_data` volume: persists Ollama models

## Files

- `docker-compose.yml` - OpenClaw + Ollama stack
- `Dockerfile.openclaw` - container image for OpenClaw CLI
- `.env.example` - required environment variables

## Prerequisites

- Docker Desktop running in Linux container mode
- Telegram bot token from BotFather
- OpenAI API key (if your OpenClaw agent/model setup requires it)

## Setup

1. Create `.env`:

```bash
cp .env.example .env
```

2. Fill values in `.env`:

- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `OLLAMA_BASE_URL=http://ollama:11434`
- `OLLAMA_MODEL=qwen2.5:7b` (recommended for your current Windows laptop profile)
- Optional MiniMax routing:
  - `MINIMAX_API_KEY`
  - `MINIMAX_BASE_URL=https://api.minimax.io`
  - `MINIMAX_MODEL=MiniMax-M2.5`

3. Build and start:

```bash
docker compose up --build -d
```

4. Pull an Ollama model (first time):

```bash
docker compose exec ollama ollama pull qwen2.5:7b
```

## Onboard OpenClaw (inside container)

Run onboarding once to initialize OpenClaw config in the persistent volume:

```bash
docker compose exec openclaw openclaw onboard
```

Then restart gateway:

```bash
docker compose restart openclaw
```

## Telegram pairing and approval

If your policy requires pairing:

```bash
docker compose exec openclaw openclaw pairing list telegram
docker compose exec openclaw openclaw pairing approve telegram <CODE>
```

## Operations

Start:

```bash
docker compose up -d
```

Restart:

```bash
docker compose restart openclaw
```

Logs:

```bash
docker compose logs -f openclaw
docker compose logs -f ollama
```

Stop:

```bash
docker compose down
```

Clean reset (also deletes OpenClaw config + Ollama models):

```bash
docker compose down -v
docker compose up --build -d
```

## Verify it is OpenClaw mode

```bash
docker compose ps
```

You should see `openclaw-gateway` and `openclaw-ollama`.

## Provider routing in chat

- Prefix prompts to force provider routing:
  - `ollama: <prompt>`
  - `gemini: <prompt>`
  - `minimax: <prompt>`
  - `azure: <prompt>`
- Or set `DEFAULT_PROVIDER` to one of: `ollama`, `gemini`, `minimax`, `azure`.

## References

- https://openclaw.im/docs/channels/telegram
- https://openclaw.im/docs/start/wizard
- https://openclaw.im/docs/gateway/configuration
