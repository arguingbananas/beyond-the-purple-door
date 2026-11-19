# Beyond Castle Wolfenstein purple-door project

Patches and tools that make the purple door in room `$3C` passable, plus headless Apple2TS control.
Read `docs/Project-Notes.md` first; the README has setup.

## Environment
- Python 3.12 (stdlib only), Node 22+ (tested on 24), shellcheck. Emulator tools also need Chromium
  and an Apple2TS web build in `a2ts-web/`, extracted from `apps/Apple2TS.AppImage`
  (see `tools/README-a2ts.md`). `apps/` and `a2ts-web/` are gitignored. Optional: CiderPress II in
  `apps/cp2/` for the filesystem check in `tools/verify.sh` (`cp2 test` alone reports "no failures" for a
  damaged DOS filesystem, so use `tools/cp2_check.py`, which compares against the original image).
- The game image is not in this repo and must never be committed. Work on copies; never modify the
  original 4am image.
- Dev tools: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && npm ci`

## Commands
- Smoke test (about 1 s, needs the game image): `tools/verify.sh`
- Full suite: `tools/test.sh`
- Lint and format check: `tools/lint.sh` (add `--fix` to apply fixes)
- Dependency audit: `tools/audit.sh`
- Emulator: `tools/bcw_up.sh` / `tools/bcw_down.sh`
- Bridge actions and payloads for scripting the emulator: `docs/Bridge-API.md`
- Optional overrides (`BCW_IMAGE`, `CP2`, `A2TS_DIST`, `A2TS_BRIDGE`): see the table in `README.md`
- Enable the pre-commit hook (lint, tests, secret scan): `tools/install-hooks.sh`

## Files
- Required: `README.md`, `LICENSE`, `.gitignore`, `requirements-dev.txt`, `package-lock.json`
- Patchers import each other: keep `patches/apply_bcw_*.py` together; run them from `patches/`.
- Scripts that read disk images: `python3 -I script.py args`.

## Rules
- Secrets and personal data never go in code, logs or commits.
- Third-party content: never commit game images, saved states, or Apple2TS builds.
- Tests must not contact live services; the only network use is `tools/audit.sh` and installs.
- Do not use `pkill -f` from Claude Code (it matches the tool's own shell); `tools/bcw_down.sh`
  stops the bridge by PID.
- This repo is self-contained: its git root is this folder. Never add files, history or references
  from other projects in the parent directory, and never run git commands against the parent.
- Push only `main`. Claude Code may create local `refs/agents/*` checkpoint refs; they are not part
  of the project, so never push with `--all` or `--mirror`.

## Definition of done
Sanity (`tools/verify.sh`) and full tests pass, `tools/lint.sh` is clean, `tools/audit.sh` shows no new
high-severity findings, and the README is updated if behavior changed.
