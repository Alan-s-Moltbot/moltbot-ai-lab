#!/bin/sh
set -eu

export DISPLAY="${DISPLAY:-:1}"

/opt/openclaw/bin/init-openclaw-config.sh

exec openclaw gateway --allow-unconfigured
