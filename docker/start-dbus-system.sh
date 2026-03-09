#!/bin/sh
set -eu

mkdir -p /run/dbus
dbus-uuidgen --ensure

exec dbus-daemon --system --nofork --nopidfile
