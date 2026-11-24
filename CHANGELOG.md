# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/);
there are no tagged releases yet.

## Unreleased

### Added
- `reference/cabinet-room.webp`: a 64 s recording of the patched cabinet room (player, guard and
  the now-passable purple door), shown at the top of the README.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), issue and pull request templates.
- End-of-support dates for Node, Python and the CI image, and the steps to move on, in the README.
- `SECURITY.md` says what the project does not defend against.
- Headless Apple2TS control through its built-in remote-control bridge: `tools/a2ts_bridge.mjs`,
  `tools/a2ts_ctl.mjs`, `tools/bcw_up.sh`, `tools/bcw_down.sh` (see `tools/README-a2ts.md`).
- `tools/verify.sh` and `tools/ips_apply.py` to rebuild patched images and check hashes, plus an
  optional CiderPress II filesystem check (`tools/cp2_check.py`, skipped when `apps/cp2/cp2` is absent)
  that compares each rebuilt image with the original: same notes, usage counts and files. It does
  not rely on `cp2 test` alone, which reports "no failures" for a damaged DOS filesystem.
- `docs/Third-Party.md`: every third-party program, tool and piece of content, with version,
  license and link (licenses checked against each upstream at the version used).
- `docs/Bridge-API.md`: every bridge action and payload, with the ones this project has verified.
- Test suite (`tools/test.sh`): Python `unittest`, Node `node:test`, and the hash checks.
- Lint and audit tooling: `tools/lint.sh`, `tools/audit.sh`, pinned dev dependencies.
- Pre-commit hook (`.githooks/`, enabled with `tools/install-hooks.sh`): lint, tests, and a gitleaks
  secret scan of staged changes when gitleaks is installed.
- README, LICENSE (MIT), `docs/Project-Notes.md`, `docs/ARCHITECTURE.md`, `ROADMAP.md`,
  `CONTRIBUTING.md`, `CLAUDE.md`, examples, GitHub Actions CI and Dependabot configuration.

### Removed
- **The global terminal-barrier patch** (`apply_bcw_terminal_patch.py`, `bcw-terminal-barrier.ips`,
  `docs/Terminal-Barrier-Patch.md`): obsolete now that the local patch opens the purple door in room
  `$3C` alone. Its DOS 3.3 catalog and sector helpers, which the local patcher used, moved to
  `patches/dos33.py`. The patch remains in git history.

### Changed
- **Node 24 or newer is now required** (was 22+; Node 22 reaches end of life on 2027-04-30).
- The Apple2TS desktop app is pinned to v1.6.9 with its SHA-256 in `tools/README-a2ts.md`: v1.7.1
  is broken, and the AppImage replaces itself with the latest release when launched, so it is run
  from an extracted copy.
- `.gitignore` also covers `.env`, key files, saved states (`*.a2ts`) and editor files.
- **Terminal-barrier patch no longer opens a door in room 15.** Its two map edits (`CASTLE` and
  `BACKUP` file offset `$1026`, `$15` to `$35`) came from mistaking that door for the purple one.
  The patch is now the three collision edits in `@FHR` (5 bytes); the patched image hash changed
  from `758ba06d...` to `483ecb6c...`. The local and saved-game patches never had this edit.
- Removed the PDF copies of the patch docs: they were exported in October and had drifted from the
  Markdown, which GitHub renders.
- Boot-tested the images built from the IPS files: all three reach the title screen and the
  saved-game image resumes into room `$3C`. Docs give the tested menu steps (Esc only if the attract
  demo is running).
- `tools/bcw_up.sh` checks that the saved state and web build exist before starting, and encodes the
  state path as proper JSON.
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
- The headless Chromium makes no outbound connections: host names other than `127.0.0.1` do not
  resolve, and its background services are off. Before, its sign-in, time-check and model-download
  services reached Google.
- From CodeQL: the bridge refuses a `timeoutMs` outside 1 ms to 10 minutes and answers a bad request with
  a fixed message (details go to its log, not the client).

## Earlier history (before this changelog)
- Terminal-barrier patch (global collision change) and the local purple-door patch (room `$3C` only),
  with write-ups, IPS files and a saved-game variant.
