# Contributing

Thanks for looking. This is a small hobby project; issues and pull requests are welcome.

## Setup
```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && npm ci
```
You need Python 3.12, Node 22+, and `shellcheck`. Supply your own game image (see the README); the
tests that need it skip themselves without it.

## Git hook (recommended)
```sh
tools/install-hooks.sh   # once per clone: runs lint, tests and a secret scan on every commit
```
The secret scan uses [`gitleaks`](https://github.com/gitleaks/gitleaks) if it is installed and is
skipped with a note if not. GitHub secret scanning also applies once the repo is public.

## Before you open a pull request
```sh
tools/lint.sh      # shellcheck, ruff, eslint, prettier; tools/lint.sh --fix applies fixes
tools/test.sh      # unit tests, bridge tests, and (with the game image) the hash checks
```
Both must be clean. CI runs the same commands, minus the game-image checks.

## Conventions
- Branch `main`. One logical change per commit; subject in the imperative mood, at most 72 characters,
  with a body that says why when it is not obvious.
- Add or update tests with the change. Patchers must never modify their input image and must refuse
  to overwrite an existing output file.
- Update `README.md` when behavior changes, and `CHANGELOG.md` for anything a user would notice.
- Keep the tools free of runtime dependencies (Python standard library, built-in Node modules).
  Dev-only dependencies go in `requirements-dev.txt` / `package.json` and the lockfiles.

## Never commit
Game images (`.dsk` and friends), emulator saved states, Apple2TS builds, secrets, or personal data.
Those paths are in `.gitignore`; do not force-add them.

## Manual check of the emulator tools
The emulator route cannot run in CI (it needs Chromium, an Apple2TS build and a saved state).
After touching `tools/a2ts_*` or `tools/bcw_*.sh`, run `tools/bcw_up.sh`, then
`examples/read_room_byte.sh` (expect `"bytes":[60]`), then `tools/bcw_down.sh`.

## Reporting security problems
See [SECURITY.md](SECURITY.md).
