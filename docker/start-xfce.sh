#!/bin/sh
set -eu

export DISPLAY="${DISPLAY:-:1}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-root}"
export NO_AT_BRIDGE="${NO_AT_BRIDGE:-1}"

mkdir -p "${XDG_RUNTIME_DIR}"
chmod 700 "${XDG_RUNTIME_DIR}"

display_socket="/tmp/.X11-unix/X${DISPLAY#:}"
while [ ! -S "${display_socket}" ]; do
  sleep 1
done

exec dbus-launch --exit-with-session xfce4-session
