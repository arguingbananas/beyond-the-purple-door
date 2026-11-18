# Beyond Castle Wolfenstein: purple door

Patches and tools for making the purple door in the terminal room of *Beyond Castle Wolfenstein*
(Muse Software, 1984, Apple II, DOS 3.3) passable, plus a way to drive the Apple2TS emulator in the
background to test them.

- **Patches** take a disk image of the game in, and write a new, patched image out. Nothing here is
  the game itself.
- **Tools** rebuild and verify the patched images by hash, and run Apple2TS headless (no window) so a
  script can restore a saved state, read memory and capture screenshots.

Who it is for: people modding or studying the game, and anyone who wants to script Apple2TS.

## You supply the game

The game image is copyrighted and is **not** in this repo. The patches target the 4am crack of the
game: a raw DOS-order, 143,360-byte, 35-track `.dsk` with SHA-256 starting `5898ae8f`. Put it at
`Beyond Castle Wolfenstein (4am crack)/Beyond Castle Wolfenstein (4am crack).dsk` in the repo root
(gitignored), or point `BCW_IMAGE` at it. Play the patched copy and keep the original untouched.

## Quick start

Requirements: Python 3.12 (standard library only), Node 22 or newer (tested on 24), and `shellcheck`.
Chromium and an Apple2TS web build are needed only for the emulator tools (see
[`tools/README-a2ts.md`](tools/README-a2ts.md)).

```sh
tools/verify.sh                      # rebuild every patched image from your game image and check hashes (~1 s)
tools/test.sh                        # full suite: Python tests, Node tests, hash check
cd patches
python3 apply_bcw_purple_door_patch.py ../"Beyond Castle Wolfenstein (4am crack)"/*.dsk /tmp/door.dsk
```

That last command writes a new image with the local purple-door patch; the input is not modified.
The result is expected to hash to `3d843c2c...`.

Dev tooling is optional and has no effect on the tools themselves:

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && npm ci   # once
tools/lint.sh            # shellcheck, ruff, eslint, prettier (add --fix to apply fixes)
tools/audit.sh           # pip-audit and npm audit on the dev dependencies
```

## What is in here

| Path | Contents |
|---|---|
| `patches/` | Python patchers and IPS files. The two patchers import each other, so keep them together. |
| `docs/` | How the door is made solid, what each patch changes, project notes, untried ideas. |
| `tools/` | `verify.sh`, `test.sh`, `ips_apply.py`, and the headless emulator scripts. |
| `tests/` | Unit tests (`unittest` and `node:test`). Tests that need the game image skip without it. |
| `examples/` | Small runnable scripts: patch an image, read the room number from the emulator. |
| `reference/` | Screenshots of the room. |
| `apps/`, `a2ts-web/` | Local only and gitignored: the Apple2TS AppImage, its web build and saved emulator states. |

Start with [`docs/Project-Notes.md`](docs/Project-Notes.md); [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains how the pieces fit, and [`ROADMAP.md`](ROADMAP.md) lists what is next. The local patch is the preferred one: it
affects only room `$3C`, but guards can walk through the door too. The global terminal-barrier patch
changes shared collision code and probably opens other walls.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md); in short:

- Branch `main`. One logical change per commit; subject in the imperative mood, at most 72 characters.
- Run `tools/test.sh` and `tools/lint.sh` before committing; they should be clean.
- Never commit game images, saved states or emulator builds (`.dsk`, `a2ts-web/`, ... are gitignored).
- Secrets and personal data never go in code, logs or commits.

## License and credits

The code and documentation in this repo are [MIT licensed](LICENSE). That does not cover the game,
which belongs to its rights holders, or the 4am crack of it ([archive.org](https://archive.org/details/Passport4am)).
The screenshots in `reference/` and `tools/refs/` are frames from the game, included to document the
room and to drive the emulator menus.

The emulator tools use [Apple2TS](https://github.com/ct6502/apple2ts) by Chris Torrence (CT6502),
which is MIT licensed. Its web build is downloaded separately and is not redistributed here.
