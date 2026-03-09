#!/bin/sh
set -eu

export DISPLAY="${DISPLAY:-:1}"
export VNC_PORT="${VNC_PORT:-5901}"
export SCREEN_GEOMETRY="${SCREEN_GEOMETRY:-1440x900x24}"

mkdir -p /root/.vnc

if [ -z "${VNC_PASSWORD:-}" ]; then
  VNC_PASSWORD="change-me"
  echo "WARNING: VNC_PASSWORD is not set; using insecure fallback password 'change-me'" >&2
fi

x11vnc -storepasswd "${VNC_PASSWORD}" /root/.vnc/passwd >/dev/null

display_socket="/tmp/.X11-unix/X${DISPLAY#:}"
while [ ! -S "${display_socket}" ]; do
  sleep 1
done

exec x11vnc \
  -display "${DISPLAY}" \
  -rfbport "${VNC_PORT}" \
  -forever \
  -shared \
  -rfbauth /root/.vnc/passwd
