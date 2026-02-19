# Moltbot AI Lab

This repository is configured for a **Linux CLI-only OpenClaw gateway** with Telegram control and **MiniMax as the agent model backend**.

## Architecture

- `openclaw` service: runs `openclaw gateway`
- `openclaw_data` volume: persists OpenClaw onboarding/config
- No UI services (no VNC/noVNC)
- No Ollama sidecar service

## Files

- `docker-compose.yml` - CLI-only OpenClaw stack
- `Dockerfile.openclaw` - lightweight OpenClaw CLI image
- `.env.example` - required MiniMax + Telegram environment variables

## Prerequisites

- Linux host with Docker Engine + Docker Compose plugin
- Telegram bot token from BotFather
- MiniMax API key

## Setup

1. Create `.env`:

```bash
cp .env.example .env
```

2. Fill values in `.env`:

- `TELEGRAM_BOT_TOKEN`
- `MINIMAX_API_KEY`
- Optional overrides:
  - `MINIMAX_BASE_URL=https://api.minimax.io`
  - `MINIMAX_MODEL=MiniMax-M2.5`

3. Build and start:

```bash
docker compose up --build -d
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
```

Stop:

```bash
docker compose down
```

Clean reset (also deletes OpenClaw config):

```bash
docker compose down -v
docker compose up --build -d
```

## Verify it is CLI-only OpenClaw mode

```bash
docker compose ps
```

You should only see `openclaw-gateway`.

## Provider routing in chat

Use MiniMax as the default provider for your bot runtime (`DEFAULT_PROVIDER=minimax`) and configure `MINIMAX_API_KEY`.

## References

- https://openclaw.im/docs/channels/telegram
- https://openclaw.im/docs/start/wizard
- https://openclaw.im/docs/gateway/configuration
