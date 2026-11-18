# Beyond Castle Wolfenstein purple-door project

Read `docs/Project-Notes.md` first: goal, memory map, patch bytes and verification state.

- The game images are not in this repo. Never modify the original 4am image; every patch starts from
  it, so work on copies.
- Patchers are Python 3 standard library only. Run `tools/verify.sh` after any change to `patches/`.
- Scripts that read disk images: run them as `python3 -I script.py args`. The two patchers import each
  other, so run those from `patches/` without `-I`.
- Emulator control (headless, background): `tools/README-a2ts.md`. Do not use `pkill -f` from Claude
  Code; it matches the tool's own shell. `tools/bcw_down.sh` kills by PID.
