#!/usr/bin/env bash
# Check the dev dependencies for known vulnerabilities (contacts the PyPI and npm advisory services).
# The tools themselves have no runtime dependencies, so this covers dev tooling only.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$here"
"$here/.venv/bin/pip-audit" -r requirements-dev.txt --no-deps --disable-pip
npm audit
