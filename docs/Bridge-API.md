# Apple2TS bridge API

How scripts drive the headless emulator: `tools/a2ts_ctl.mjs` sends an **action** and a JSON
**payload** to `tools/a2ts_bridge.mjs`, which relays it to the Apple2TS page and returns the reply.

```sh
node tools/a2ts_ctl.mjs <action> '<json payload>' [--png out.png]
curl -s 127.0.0.1:8765/api/cmd -d '{"action":"getStatus","payload":{}}'
```

The actions are Apple2TS's own remote-control commands, read from its source
(`src/ui/api/remotecontrol.ts` in Apple2TS 1.6.9, via the source maps in the release). They are not
a documented, stable Apple2TS API and may change between versions. **Verified** marks the actions
this project has actually used; the rest are listed from the source and untested here.

## Bridge HTTP endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/cmd` `{action, payload, timeoutMs?}` | Send one action and wait for the reply. Returns `{ok: true, result}` or `{ok: false, error}`. Default wait 120 s; `timeoutMs` outside 1 to 600000 (10 min) is refused. A bad request is a 400 `{error: "bad request"}`. |
| `GET /api/state` | The last status the page posted (it sends one every 2 s and after each command). |
| `/api/client/connect`, `/api/client/events`, `/api/client/state`, `/api/client/reply` | Used by the Apple2TS page itself (it connects back when loaded with `?remoteControl=1`). |
| `GET /disks/game.dsk` | The `--disk` image, served read-only so the page can load it via `#game.dsk`. |
| Anything else | Static files from the web build (`--dist`). |

The bridge binds `127.0.0.1` only and answers 403 to a foreign `Host` or `Origin` header.

`a2ts_ctl.mjs` extras: in a payload, `{"file": "path"}` is replaced by that file's contents as
`dataBase64`; `--png out.png` writes a `captureScreen` result to a file; `waitScreen ref.png [sec]`
polls until the screen is byte-identical to a reference frame.

## Conventions

- Addresses and lengths are plain numbers (JSON has no hex): `$4050` is `16464`.
- `space` is `"main"` or `"aux"`; `auxBank` selects a RamWorks bank for `"aux"`.
- Most actions reply with the full status object (see `getStatus`).
- Run modes (`RUN_MODE`): `0` idle, `-1` running, `-2` paused, `-3` boot, `-4` reset.

## Status and memory

| Action | Payload | Notes |
|---|---|---|
| `getStatus` **verified** | `{}` | `machine` (runMode, execution, speedMode, machineName, CPU state, text page, stack, soft switches, `memoryAvailable`), `ui`, `drives`. |
| `getMemoryView` **verified** | `{address, length, space, auxBank?}` | Returns `bytes`. **Only while paused**; otherwise an error. |
| `getMemory` | `{}` | Whole memory dump plus CPU state. |
| `findMemory` | `{address, length, space, bytes, maxMatches?}` | Search for 1 to 32 bytes; default 32 matches. |
| `setMemory` | `{address, value}` | One byte. |
| `writeMemory` | `{address, data: [bytes]}` | Several bytes. |
| `setMemoryWriteWatchpoint` | `{address, length, space, auxBank?}` | Pauses when the range is written (how the door's collision writer at `$5D33` was found, in the desktop debugger). |
| `clearMemoryWriteWatchpoint` | `{}` | |
| `compareSessionMemory` | `{snapshotId, address, length, space?, auxBank?, maxChanges?}` | Diff memory against a session snapshot. |

## Execution and CPU

| Action | Payload | Notes |
|---|---|---|
| `setRunMode` **verified** | `{runMode}` | See run modes above. `bcw_up.sh` uses `-1` and `-2`. |
| `setSpeedMode` | `{speedMode}` | Numeric; `0` is normal speed. Other values not checked here. |
| `stepInto`, `stepOver`, `stepOut` | `{}` | Single-step while paused. |
| `setCpuState` | `{state}` | Set registers. |
| `getBreakpoints` / `setBreakpoints` | `{}` / `{breakpoints: [...]}` | |
| `setDebug`, `setShowDebugTab` | `{enabled}` | |
| `setSoftSwitches` | `{addresses: [...]}` | |

## Keyboard and input

| Action | Payload | Notes |
|---|---|---|
| `sendKeys` **verified** | `{keys, timeoutMs}` | Delivers each key only after the program has read the previous one. Use `"\r"` for Return, `"\u001b"` for Esc. |
| `runInputSequence` **verified** | `{phases: [{when?, keys}], final, stopConditions?, timeoutMs, startExecution?}` | Keys wait for memory conditions. 1 to 16 phases, at most 32 keys each and 64 in total; `timeoutMs` up to 120000; up to 8 named `stopConditions`. Outcome: `completed`, `timeout`, `cancelled`, `unexpected_stop`, `condition_triggered` or `input_busy`. |
| `cancelInputSequence` | `{}` | |
| `keypress` | `{key, release?}` | One key (character or code); released unless `release` is `false`. |
| `setKeyboardState` | `{key, isDown, repeat}` | Hold or release a key. |
| `pasteText` | `{text}` | Type text. |
| `appleKey` | `{side: "left"\|"right", pressed?}` | Open/closed Apple keys. |
| `mouseEvent` | `{x, y, buttons}` | |

A memory condition (`when`, `final`, a stop condition's `when`) is a predicate
`{address, bytes: [1 to 32 values], mask?, space, auxBank?}`, or `{all: [up to 8 predicates]}`.
Example used by this project: Return, then done when the room byte `$4050` is `$3C`:

```json
{"phases": [{"keys": "\r"}], "final": {"address": 16464, "bytes": [60], "space": "main"}, "timeoutMs": 100000}
```

## Screen

| Action | Payload | Notes |
|---|---|---|
| `captureScreen` **verified** | `{}` | `{mimeType: "image/png", dataBase64, width, height}`. Frames of the same screen are byte-identical, which `waitScreen` relies on. |
| `setColorMode`, `setMonitorMode` | `{colorMode}` / `{monitorMode}` | |

## Saved states and snapshots

| Action | Payload | Notes |
|---|---|---|
| `exportSaveState` **verified** | `{includeSnapshots}` | `{filename, mimeType, dataBase64}`: a `.a2ts` JSON state, disks included. |
| `importSaveState` **verified** | `{dataBase64}` | Restore a state. Can fail silently right after the page connects; `bcw_up.sh` retries and checks memory. |
| `createSessionSnapshot` / `restoreSessionSnapshot` | `{snapshotId}` | Named in-memory snapshots. |
| `createSnapshot`, `getSnapshots`, `stepSnapshotBack`, `stepSnapshotForward` | `{}` | Time-travel snapshots. |
| `activateSnapshot` | `{snapshotId}` | Jump to a time-travel snapshot, e.g. `"snap:3"`. |

## Disks, programs and machine

| Action | Payload | Notes |
|---|---|---|
| `mountDisk` | `{dataBase64, filename, driveIndex}` | **Rejected by the emulator worker** in this project's tests; load disks with the `#name` URL fragment instead (what `--disk` does). |
| `mountDiskFromUrl` | `{url, driveIndex}` | **Failed** against this bridge in testing; same workaround. Sets the machine to boot. |
| `ejectDisk` | `{driveIndex}` | |
| `setDriveWriteProtected` | `{driveIndex, isWriteProtected}` | |
| `loadBinary` | `{dataBase64, address?}` | Default address `$300`. |
| `runBinary` | `{dataBase64, address?, entryAddress?}` | |
| `mountBinaryBlock` | | Deprecated; use `loadBinary` / `runBinary`. |
| `mountBasicText` | `{text, autoRun?}` | Types a BASIC program, then `RUN` if it has line numbers. |
| `setMachineName`, `setRamWorks` | `{machineName}` / `{size}` | |
