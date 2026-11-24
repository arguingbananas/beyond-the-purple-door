#!/usr/bin/env bash
# Run the whole suite: Python unit tests, Node bridge tests, then the hash-checked patch rebuild.
# Quick smoke test (about a second, needs the game image): tools/verify.sh
# The tests that need the game image skip themselves if it is absent (set BCW_IMAGE or see tests/test_patchers.py).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$here"
python3 -I -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "tools/test.sh: needs Python 3.11 or newer")'
python3 -I -m unittest discover -s tests -v
node --test tests/*.mjs
if [ -f "${BCW_IMAGE:-Beyond Castle Wolfenstein (4am crack)/Beyond Castle Wolfenstein (4am crack).dsk}" ]; then
  tools/verify.sh "${BCW_IMAGE:-}"
else
  echo "skipped tools/verify.sh: game image not found"
fi
