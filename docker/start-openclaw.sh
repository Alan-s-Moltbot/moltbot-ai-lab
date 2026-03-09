#!/bin/sh
set -eu

export DISPLAY="${DISPLAY:-:1}"

exec openclaw gateway --allow-unconfigured
