# Architecture

## Two halves
1. **Patching** (`patches/`): pure Python. A patcher reads a DOS 3.3 disk image, finds the target
   files through the catalog and track/sector lists, checks the original bytes, and writes a *new*
   image. IPS files are the same edits for the standard image at fixed offsets. `tools/verify.sh`
   proves the patchers and the IPS files agree by hash.
2. **Emulator control** (`tools/a2ts_*`, `tools/bcw_*.sh`): Node and shell. Used to test patches in
   a running emulator without a window.

## How the patch works
See `docs/Project-Notes.md` and `docs/Purple-Door-Local-Patch.md`: the door is object record `$40A0`;
its collision bytes are written into `$4200,X` and `$4208,X` by `^THINGS` at `$5D2D`. A 24-byte stub in
unused padding after `@FHR` returns zero for that one cell in room `$3C`.

## Emulator control

```
 your script --HTTP--> a2ts_bridge.mjs <--SSE / POST-- headless Chromium
 (a2ts_ctl.mjs)          127.0.0.1:8765                 running Apple2TS web build
   POST /api/cmd         serves the web build            ?remoteControl=1
                         relays commands, returns replies
```

- Apple2TS's web build has a built-in remote-control client (enabled by `?remoteControl=1`). It
  connects back to the server that served it, receives commands over server-sent events, and posts
  replies. `a2ts_bridge.mjs` is a small stand-in for that server and adds `/api/cmd` so scripts can
  send a command and wait for its reply.
- `bcw_up.sh` starts the bridge with `--chromium`, imports a saved emulator state (the menus are
  skipped), runs two seconds so the screen draws, pauses, and checks the room byte.
- The bridge binds `127.0.0.1`, rejects foreign `Host` and `Origin` headers, and records its PID so
  `bcw_down.sh` stops exactly that process. Chromium runs in its own process group so the bridge can
  stop it and delete its temporary profile.
- Nothing leaves the machine: Chromium is started with `--host-resolver-rules` that resolve no host
  name except `127.0.0.1`, plus flags that turn off its background services. Without that, its own
  services (account sign-in, a time check, model downloads) contact Google even in headless mode.
  The Apple2TS page itself requests nothing external on load.
- Emulator state, the web build and the game image are all gitignored; see `tools/README-a2ts.md`.
- Every action and payload the bridge relays: `docs/Bridge-API.md`.

## Tests
- `tests/test_ips_apply.py`, `tests/test_patchers.py`: Python `unittest`; synthetic images for error
  paths, the real image (when supplied) for hash and behavior checks.
- `tests/test_bridge.mjs`: `node:test` against a throwaway bridge with a fake emulator client.
- `tools/verify.sh`: the fast end-to-end hash check; `tools/test.sh` runs everything.
