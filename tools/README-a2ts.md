# Driving Apple2TS in the background

No window, no foreground focus. Apple2TS's web build runs in headless Chromium and takes commands
through its built-in remote-control bridge (`?remoteControl=1`, see `src/ui/api/remotecontrol.ts` in
the AppImage's source maps).

## One-time setup (gitignored folders at the repo root; nothing here is committed)
- `apps/Apple2TS.AppImage`: the Apple2TS desktop app **v1.6.9**. Download `Apple2TS.AppImage` from
  the [v1.6.9 release](https://github.com/ct6502/apple2ts-app/releases/tag/v1.6.9) and check that its
  SHA-256 equals the digest GitHub shows for that asset
  (`52f5eb415b12dbebf694dcd97999d0ef152ff2b51c42e84d8b1fb3e984aa3f26`). Do not use v1.7.1: its
  AppImage ships the web source instead of the built `apple2ts-dist/dist/` and hangs on the splash
  screen. It is the source of the web build below, and of a window for playing by hand.
- **The AppImage updates itself when launched** (it downloads the latest release and replaces its
  own file). Never run it directly. Extract it once into `apps/Apple2TS-1.6.9/` (run
  `../Apple2TS.AppImage --appimage-extract` inside that folder) and play with
  `apps/Apple2TS-1.6.9/squashfs-root/AppRun <copy.dsk>`; started that way the updater finds no
  AppImage and does nothing. The game writes to its disk, so play a copy.
- `apps/cp2/` (optional): [CiderPress II](https://github.com/fadden/CiderPress2) v1.2.0, used by
  `tools/verify.sh` to check each rebuilt image. Download `cp2_1.2.0_linux-x64_sc.zip` from its
  GitHub release, check that its SHA-256 equals the digest GitHub shows for that asset
  (`8c8748a0b484b4a778354146ffe4b6b44527f066b440a2e7bccebf4050948981`), and unzip it into
  `apps/cp2/`. `cp2 test` alone is not enough: it reports "no failures" and exits 0 for a damaged
  DOS filesystem. `tools/cp2_check.py` compares each image with the original instead (see its header).
- `a2ts-web/dist/`: the web build. In an empty scratch folder run
  `<repo>/apps/Apple2TS.AppImage --appimage-extract`, then copy
  `squashfs-root/resources/apple2ts-dist/dist` to `a2ts-web/dist`.
- `a2ts-web/states/bcw-cabinet-room-local-v3.a2ts`: an exported emulator state (paused in room `$3C`,
  local patch v3 disk inside). Remake it whenever the patched disk changes (below).

## Everyday use
```sh
tools/bcw_up.sh        # ~10 s: headless emulator, state restored, PAUSED in the cabinet room
node tools/a2ts_ctl.mjs captureScreen --png /tmp/room.png
node tools/a2ts_ctl.mjs getMemoryView '{"address":16464,"length":1,"space":"main"}'   # needs PAUSED
node tools/a2ts_ctl.mjs setRunMode '{"runMode":-1}'    # run (-2 pause, -3 boot, -4 reset)
tools/bcw_down.sh
```
`a2ts_ctl.mjs <action> '<json payload>'` sends any bridge action (getStatus, getMemoryView, findMemory,
setMemoryWriteWatchpoint, sendKeys, runInputSequence, setSpeedMode, importSaveState/exportSaveState,
setMemory/writeMemory, stepInto/Over/Out, ...). `{"file":"path"}` in a payload is replaced by that
file's base64 as `dataBase64`. `waitScreen <ref.png> [sec]` waits for a frame byte-identical to a
reference (`tools/refs/`). Every action and its payload: [`docs/Bridge-API.md`](../docs/Bridge-API.md).

Overrides (optional): `A2TS_DIST` points `bcw_up.sh` at another web build, and `A2TS_BRIDGE`
(`host:port`) points `a2ts_ctl.mjs` at another bridge. See the table in the top-level README.

## Making a new state for a different disk (menus; verified by hand, not scripted)
1. `node tools/a2ts_bridge.mjs --dist <dist> --disk <disk.dsk> --chromium &`  (disk loads and boots via `#game.dsk`)
2. `waitScreen refs/title.png 90` (the attract demo loops; the title is only up briefly), then
   `sendKeys '{"keys":"\r"}'`, `waitScreen refs/controls.png`, `sendKeys K`,
   `waitScreen refs/options.png`, `sendKeys D` (a D sent before the options screen is lost),
   `waitScreen refs/resume-selected.png`.
3. `runInputSequence '{"phases":[{"keys":"\r"}],"final":{"address":16464,"bytes":[60],"space":"main"},"timeoutMs":100000}'`
   (done when room byte `$4050` = `$3C`), then run ~6 s, pause (`-2`) so the guard cannot catch anyone.
4. `exportSaveState '{"includeSnapshots":false}'` and write `dataBase64` to `states/<name>.a2ts`.

## Gotchas
- Fixed sleeps are unreliable (headless runs ~0.7 MHz; the attract demo steals keys). Wait on screen
  or memory conditions instead. `sendKeys` returns when the game has consumed the key.
- Memory reads only work while the emulator is paused. The room byte is set before the room is drawn.
- Right after the page connects the worker may not be ready; `bcw_up.sh` retries the import and verifies.
- Never `pkill -f` from Claude Code (it matches the tool's own shell); `bcw_down.sh` kills by PID.
- The emulator edits only its in-browser disk copy, so disk files on disk are never modified.
