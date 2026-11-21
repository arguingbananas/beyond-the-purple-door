#!/usr/bin/env bash
# Rebuild the patched images from the 4am crack and check their hashes.
# usage: tools/verify.sh [path/to/Beyond Castle Wolfenstein (4am crack).dsk]
# You supply the game image yourself; it is not in this repo. Nothing is written outside a temp dir.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
v="${1:-$here/Beyond Castle Wolfenstein (4am crack)/Beyond Castle Wolfenstein (4am crack).dsk}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
fail=0
check() { # name file expected-prefix
  got="$(sha256sum "$2" | cut -c1-8)"
  if [ "$got" = "$3" ]; then echo "ok   $1 ($got)"; else echo "FAIL $1: got $got, want $3"; fail=1; fi
}
check "4am crack image" "$v" 5898ae8f
# the patchers import each other, so run them from a scratch copy
cp "$here"/patches/apply_bcw_*.py "$tmp/"
( cd "$tmp" && python3 apply_bcw_purple_door_patch.py "$v" door.dsk >/dev/null && python3 apply_bcw_terminal_patch.py "$v" term.dsk >/dev/null )
python3 -I "$here/tools/ips_apply.py" "$v" "$here/patches/bcw-purple-door-local.ips" "$tmp/ips_door.dsk"
python3 -I "$here/tools/ips_apply.py" "$v" "$here/patches/bcw-terminal-barrier.ips" "$tmp/ips_term.dsk"
python3 -I "$here/tools/ips_apply.py" "$v" "$here/patches/bcw-purple-door-with-savegame.ips" "$tmp/ips_save.dsk"
check "local patcher"    "$tmp/door.dsk"     3d843c2c
check "local IPS"        "$tmp/ips_door.dsk" 3d843c2c
check "terminal patcher" "$tmp/term.dsk"     483ecb6c
check "terminal IPS"     "$tmp/ips_term.dsk" 483ecb6c
check "savegame IPS"     "$tmp/ips_save.dsk" ac664ef6

# Optional: CiderPress II checks that each rebuilt image is as sound a DOS 3.3 filesystem as the
# original (same notes, usage counts and files). Used when apps/cp2/cp2 (or $CP2) exists, else skipped.
# See tools/cp2_check.py for why `cp2 test` alone is not trusted.
cp2="${CP2:-$here/apps/cp2/cp2}"
if [ -x "$cp2" ]; then
  CP2="$cp2" python3 -I "$here/tools/cp2_check.py" "$v" "$tmp/door.dsk" "$tmp/term.dsk" "$tmp/ips_save.dsk" \
    || fail=1
else
  echo "skip cp2 filesystem test (apps/cp2/cp2 not found; see tools/README-a2ts.md)"
fi
exit $fail
