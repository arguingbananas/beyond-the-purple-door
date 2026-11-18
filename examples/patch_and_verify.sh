#!/usr/bin/env bash
# Example: apply the local purple-door patch to your game image and show the result's hash.
# usage: examples/patch_and_verify.sh "path/to/Beyond Castle Wolfenstein (4am crack).dsk" out.dsk
# The input is never modified; out.dsk must not already exist. Expected hash starts 3d843c2c.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ $# -eq 2 ] || { echo "usage: $0 INPUT.dsk OUTPUT.dsk" >&2; exit 2; }
in="$(realpath "$1")"
out="$(realpath -m "$2")"
(cd "$here/patches" && python3 apply_bcw_purple_door_patch.py "$in" "$out")
sha256sum "$out" | cut -c1-8
