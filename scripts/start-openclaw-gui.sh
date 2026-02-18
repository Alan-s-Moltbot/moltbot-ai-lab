#!/usr/bin/env bash
set -euo pipefail

DISPLAY_VALUE="${DISPLAY:-:99}"
XVFB_SCREEN="${XVFB_WHD:-1920x1080x24}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
VNC_PASSWORD="${VNC_PASSWORD:-}"

Xvfb "$DISPLAY_VALUE" -screen 0 "$XVFB_SCREEN" -ac +extension GLX +render -noreset &
openbox >/tmp/openbox.log 2>&1 &

if [ -n "$VNC_PASSWORD" ]; then
  x11vnc -storepasswd "$VNC_PASSWORD" /tmp/.x11vnc.pass
  x11vnc -display "$DISPLAY_VALUE" -rfbport "$VNC_PORT" -rfbauth /tmp/.x11vnc.pass -forever -shared -bg
else
  x11vnc -display "$DISPLAY_VALUE" -rfbport "$VNC_PORT" -nopw -forever -shared -bg
fi

if [ -d /usr/share/novnc ]; then
  websockify --web=/usr/share/novnc/ "$NOVNC_PORT" "localhost:$VNC_PORT" >/tmp/novnc.log 2>&1 &
fi

exec openclaw gateway
