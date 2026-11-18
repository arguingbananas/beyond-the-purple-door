#!/usr/bin/env bash
# Example: with the emulator up (tools/bcw_up.sh), read the current room number and save a screenshot.
# usage: examples/read_room_byte.sh [screenshot.png]
# Memory can only be read while the emulator is paused; bcw_up.sh leaves it paused.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ctl() { node "$here/tools/a2ts_ctl.mjs" "$@"; }
# $4050 (decimal 16464) holds the current room number; $3C (60) is the cabinet room
ctl getMemoryView '{"address":16464,"length":1,"space":"main"}' | tr -d ' \n' | grep -o '"bytes":\[[0-9]*\]'
ctl captureScreen --png "${1:-room.png}"
