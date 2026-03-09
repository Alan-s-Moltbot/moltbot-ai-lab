# Open Claw AI Lab

This repository runs an OpenClaw gateway in Docker with a lightweight Linux desktop, Brave browser, raw VNC access, and first-boot MiniMax seeding from `.env`.

## Current Stack

- Single `openclaw` service in [docker-compose.yml](/Users/alan.man/Documents/personal-workbench/openclaw-lab/docker-compose.yml)
- Custom image in [Dockerfile.openclaw](/Users/alan.man/Documents/personal-workbench/openclaw-lab/Dockerfile.openclaw)
- Base image: `node:22-bookworm-slim`
- OpenClaw install: `npm install -g openclaw@latest`
- Desktop stack: `Xvfb + XFCE + x11vnc + Brave`
- Process supervisor: `supervisord`
- OpenClaw command: `openclaw gateway --allow-unconfigured`
- First-boot config seed: writes `/root/.openclaw/openclaw.json` from `.env` when no persisted OpenClaw config exists
- Persistent config volume: `openclaw_data` mounted at `/root/.openclaw`
- Gateway port: `18789`
- VNC port: `5901`

## Repository Files

- [README.md](/Users/alan.man/Documents/personal-workbench/openclaw-lab/README.md): setup and operations
- [docker-compose.yml](/Users/alan.man/Documents/personal-workbench/openclaw-lab/docker-compose.yml): single-service stack
- [Dockerfile.openclaw](/Users/alan.man/Documents/personal-workbench/openclaw-lab/Dockerfile.openclaw): OpenClaw image build
- [.env.example](/Users/alan.man/Documents/personal-workbench/openclaw-lab/.env.example): required environment variables

## Requirements

- Docker Engine or Docker Desktop with `docker compose`
- Telegram bot token from BotFather
- MiniMax API key
- A VNC viewer client

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
- Optional: `VNC_PASSWORD` for desktop access
- Optional: `VNC_PORT` (default `5901`)
- Optional: `SCREEN_GEOMETRY` (default `1440x900x24`)

Example:

```dotenv
TELEGRAM_BOT_TOKEN=...
MINIMAX_API_KEY=...
VNC_PASSWORD=replace-this
VNC_PORT=5901
SCREEN_GEOMETRY=1440x900x24
```

If `VNC_PASSWORD` is left empty, the container starts VNC with the fallback password `change-me` and logs a warning.

## Start The Stack

Build and start the container:

```bash
docker compose up --build -d
```

The container is published as `openclaw-gateway` and exposes:

- `18789` for the OpenClaw gateway
- `5901` for VNC access

## Desktop Access

Connect your VNC client to:

```text
<docker-host>:5901
```

Authenticate with the `VNC_PASSWORD` value from `.env`.
If you do not set one, use the fallback password `change-me`.

After connection, you should see:

- an XFCE desktop session
- Brave Browser available from the application menu
- the OpenClaw gateway continuing to run in the background

If Docker is running on the same machine as your VNC client, `localhost:5901` is usually the correct host.

## First-Time Bootstrap

On a fresh `openclaw_data` volume, the container seeds `/root/.openclaw/openclaw.json` from `.env` before the gateway starts:

- `MINIMAX_API_KEY`
- `MINIMAX_BASE_URL`
- `MINIMAX_MODEL`

The seed only runs when no prior OpenClaw config exists. If the volume already contains OpenClaw state, the container preserves it and logs that bootstrap was skipped.

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

You should see a single container named `openclaw-gateway` with port mappings for `18789` and `5901`.

## Notes

- This repo now includes a lightweight desktop, Brave, and raw VNC access for native VNC clients.
- VNC is exposed directly on port `5901`; this repo does not currently include noVNC or a browser-based remote desktop.
- Brave is launched with container-safe flags so it can run inside the root-owned desktop session.
- Fresh volumes are seeded to use MiniMax from `.env`; existing persisted OpenClaw state is preserved.
- It still does not include noVNC, an Ollama sidecar, or a legacy Python bot runtime.
- The OpenClaw version is not pinned in this repo; each build installs whatever `openclaw@latest` resolves to at build time.

## Troubleshooting

- `VNC_PASSWORD is not set; using insecure fallback password 'change-me'`
  The container started VNC without an explicit password. Set `VNC_PASSWORD` in `.env` to remove the warning.
- `startxfce4: X server already running on display :0`
  This should be fixed by the new XFCE startup path. If it still appears, rebuild the image to ensure the updated supervisor/scripts are in use.
- `No API key found for provider "anthropic"`
  The mounted `openclaw_data` volume already contains prior OpenClaw state that points at Anthropic. The container preserves existing state by design. Reset the volume with `docker compose down -v` for a fresh MiniMax seed, or reconfigure the existing OpenClaw config manually.
- Telegram `groupPolicy` allowlist warning
  This is an OpenClaw channel policy warning, not a container startup failure. Configure Telegram allowlists or change the policy inside the OpenClaw config.

## References

- https://openclaw.im/docs/channels/telegram
- https://openclaw.im/docs/start/wizard
- https://openclaw.im/docs/gateway/configuration
