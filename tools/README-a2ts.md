# Driving Apple2TS in the background

No window, no foreground focus. Apple2TS's web build runs in headless Chromium and takes commands
through its built-in remote-control bridge (`?remoteControl=1`, see `src/ui/api/remotecontrol.ts` in
the AppImage's source maps).

## One-time setup (in `a2ts-web/` at the repo root, which is gitignored)
- `dist/` is the web build: `Apple2TS.AppImage --appimage-extract`, then copy
  `squashfs-root/resources/apple2ts-dist/dist`.
- `states/bcw-cabinet-room-local-v3.a2ts` is an exported emulator state (paused in room `$3C`, local
  patch v3 disk inside). Remake it whenever the patched disk changes (below).

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
reference (`tools/refs/`).

## Making a new state for a different disk (menus; verified by hand, not scripted)
1. `node tools/a2ts_bridge.mjs --dist <dist> --disk <disk.dsk> --chromium &`  (disk loads and boots via `#game.dsk`)
2. `waitScreen refs/title.png 90` (the attract demo loops; the title is only up briefly), then
   `sendKeys '{"keys":"\r"}'`, `waitScreen refs/controls.png`, `sendKeys K`, `sendKeys D`,
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
