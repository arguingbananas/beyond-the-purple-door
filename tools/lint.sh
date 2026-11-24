#!/usr/bin/env bash
# Lint and format-check everything: shellcheck, ruff (Python), eslint + prettier (Node).
# usage: tools/lint.sh          check only
#        tools/lint.sh --fix    apply safe fixes and formatting first
# Setup once: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && npm ci
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$here"
ruff="$here/.venv/bin/ruff"
if [ ! -x "$ruff" ] || [ ! -d node_modules ]; then
  echo "dev tools missing; run: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && npm ci" >&2
  exit 1
fi
if ! command -v shellcheck >/dev/null; then
  echo "shellcheck missing; install it with your package manager (e.g. sudo apt install shellcheck)" >&2
  exit 1
fi
if [ "${1:-}" = "--fix" ]; then
  "$ruff" check --fix patches tools tests
  "$ruff" format patches tools tests
  npx prettier --write tools tests
fi
shellcheck tools/*.sh examples/*.sh .githooks/pre-commit
"$ruff" check patches tools tests
"$ruff" format --check patches tools tests
npx eslint tools tests
npx prettier --check tools tests
echo "lint clean"
