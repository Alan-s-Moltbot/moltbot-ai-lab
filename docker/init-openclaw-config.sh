#!/bin/sh
set -eu

config_root="/root/.openclaw"
config_path="${config_root}/openclaw.json"
auth_profiles="${config_root}/agents/main/agent/auth-profiles.json"

mkdir -p "${config_root}"

if [ -f "${config_path}" ] || [ -f "${auth_profiles}" ]; then
  echo "OpenClaw bootstrap: existing persisted config detected; skipping MiniMax seed"
  exit 0
fi

if [ -z "${MINIMAX_API_KEY:-}" ]; then
  echo "OpenClaw bootstrap: MINIMAX_API_KEY is unset; skipping MiniMax seed"
  exit 0
fi

node <<'EOF'
const fs = require("fs");
const path = "/root/.openclaw/openclaw.json";
const config = {
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: process.env.MINIMAX_BASE_URL || "https://api.minimax.io",
        apiKey: process.env.MINIMAX_API_KEY,
        api: "openai-responses",
        models: [
          {
            id: process.env.MINIMAX_MODEL || "MiniMax-M2.5",
            name: process.env.MINIMAX_MODEL || "MiniMax-M2.5"
          }
        ]
      }
    }
  },
  agents: {
    defaults: {
      model: {
        primary: `minimax/${process.env.MINIMAX_MODEL || "MiniMax-M2.5"}`
      },
      models: {
        [`minimax/${process.env.MINIMAX_MODEL || "MiniMax-M2.5"}`]: {}
      },
      workspace: "/root/.openclaw/workspace"
    }
  }
};

fs.mkdirSync("/root/.openclaw", { recursive: true });
fs.writeFileSync(path, `${JSON.stringify(config, null, 2)}\n`);
EOF

echo "OpenClaw bootstrap: seeded fresh config with MiniMax provider from environment"
