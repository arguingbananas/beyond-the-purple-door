#!/usr/bin/env bash
# Point this clone's git at the tracked hooks in .githooks/ (runs lint, tests and a secret scan on commit).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
echo "hooks enabled: core.hooksPath = .githooks"
