# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/);
there are no tagged releases yet.

## Unreleased

### Added
- Headless Apple2TS control through its built-in remote-control bridge: `tools/a2ts_bridge.mjs`,
  `tools/a2ts_ctl.mjs`, `tools/bcw_up.sh`, `tools/bcw_down.sh` (see `tools/README-a2ts.md`).
- `tools/verify.sh` and `tools/ips_apply.py` to rebuild patched images and check hashes.
- Test suite (`tools/test.sh`): Python `unittest`, Node `node:test`, and the hash checks.
- Lint and audit tooling: `tools/lint.sh`, `tools/audit.sh`, pinned dev dependencies.
- Pre-commit hook (`.githooks/`, enabled with `tools/install-hooks.sh`): lint, tests, and a gitleaks
  secret scan of staged changes when gitleaks is installed.
- README, LICENSE (MIT), `docs/Project-Notes.md`, `docs/ARCHITECTURE.md`, `ROADMAP.md`,
  `CONTRIBUTING.md`, `CLAUDE.md`, examples, GitHub Actions CI and Dependabot configuration.

### Changed
- Repository reorganized into `patches/`, `docs/`, `reference/`, `tools/`, `tests/`.
- `apply_bcw_purple_door_patch.py` now refuses to overwrite an existing output file (including its
  own input), checks the image size, and reports errors cleanly instead of a traceback.
- `ips_apply.py` rejects truncated patches, a missing EOF marker, and writes past the end of the image.
- Patchers reformatted with ruff (formatting and import order only; output hashes are unchanged).

### Security
- GitHub Actions are pinned to commit SHAs (Dependabot keeps them current).
- Secret scan (gitleaks) of the full `main` history and the committable files: no findings.
- The bridge server rejects foreign `Host` and `Origin` headers, no longer serves sibling directories
  of the web build, and no longer crashes on malformed JSON. Chromium and its temporary profile are
  cleaned up when the bridge stops.

## Earlier history (before this changelog)
- Terminal-barrier patch (global collision change) and the local purple-door patch (room `$3C` only),
  with write-ups, IPS files and a saved-game variant.
