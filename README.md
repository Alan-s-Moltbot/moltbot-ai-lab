# Open Claw AI Lab

This repository runs a minimal Docker-based OpenClaw gateway with Telegram control and MiniMax as the model backend.

## Current Stack

- Single `openclaw` service in [docker-compose.yml](/Users/alan.man/Documents/personal-workbench/openclaw-lab/docker-compose.yml)
- Custom image in [Dockerfile.openclaw](/Users/alan.man/Documents/personal-workbench/openclaw-lab/Dockerfile.openclaw)
- Base image: `node:22-bookworm-slim`
- OpenClaw install: `npm install -g openclaw@latest`
- Container command: `openclaw gateway --allow-unconfigured`
- Persistent config volume: `openclaw_data` mounted at `/root/.openclaw`
- Gateway port: `18789`

## Repository Files

- [README.md](/Users/alan.man/Documents/personal-workbench/openclaw-lab/README.md): setup and operations
- [docker-compose.yml](/Users/alan.man/Documents/personal-workbench/openclaw-lab/docker-compose.yml): single-service stack
- [Dockerfile.openclaw](/Users/alan.man/Documents/personal-workbench/openclaw-lab/Dockerfile.openclaw): OpenClaw image build
- [.env.example](/Users/alan.man/Documents/personal-workbench/openclaw-lab/.env.example): required environment variables

## Requirements

- Docker Engine or Docker Desktop with `docker compose`
- Telegram bot token from BotFather
- MiniMax API key

## Configuration

Create your local env file:

```bash
cp .env.example .env
```

Set these values in `.env`:

- `TELEGRAM_BOT_TOKEN`
- `MINIMAX_API_KEY`
- Optional: `MINIMAX_BASE_URL` (default `https://api.minimax.io`)
- Optional: `MINIMAX_MODEL` (default `MiniMax-M2.5`)

## Start The Stack

Build and start the gateway:

```bash
docker compose up --build -d
```

The container is published as `openclaw-gateway` and exposes port `18789`.

## First-Time Onboarding

The image starts OpenClaw with `--allow-unconfigured`, but initial setup is still manual. Run onboarding once to create the persistent OpenClaw config:

```bash
docker compose exec openclaw openclaw onboard
```

Then restart the service:

```bash
docker compose restart openclaw
```

Because `/root/.openclaw` is stored in the `openclaw_data` volume, onboarding normally only needs to be done once.

## Telegram Pairing

If Telegram pairing approval is required:

```bash
docker compose exec openclaw openclaw pairing list telegram
docker compose exec openclaw openclaw pairing approve telegram <CODE>
```

## Common Commands

Start an existing stack:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f openclaw
```

Restart:

```bash
docker compose restart openclaw
```

Stop:

```bash
docker compose down
```

Reset everything, including saved OpenClaw config:

```bash
docker compose down -v
docker compose up --build -d
```

## Verify

Check the running service:

```bash
docker compose ps
```

You should see a single container named `openclaw-gateway`.

## Notes

- This repo does not include a GUI, VNC/noVNC, Ollama sidecar, or legacy Python bot runtime.
- The OpenClaw version is not pinned in this repo; each build installs whatever `openclaw@latest` resolves to at build time.

## References

- https://openclaw.im/docs/channels/telegram
- https://openclaw.im/docs/start/wizard
- https://openclaw.im/docs/gateway/configuration
