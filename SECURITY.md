# Security policy

This repo contains disk-image patchers and local development tooling; it runs no public service.
The emulator bridge (`tools/a2ts_bridge.mjs`) listens on `127.0.0.1` only and rejects foreign
`Host` and `Origin` headers. The headless Chromium it starts is blocked from resolving any other
host, so it makes no outbound connections.

What this does **not** defend against:

- Other programs running as you, or other users on the same machine: the bridge has no
  authentication, so any local process that can reach `127.0.0.1:8765` can drive the emulator
  (read and write its memory, load states). Stop it with `tools/bcw_down.sh` when you are done.
- A hostile disk image: the patchers check the image size, the DOS catalog and the exact bytes they
  replace, and refuse anything else, but they are not hardened parsers and are not fuzzed. Patch
  images you trust.
- Upstream software: Apple2TS, Chromium and CiderPress II are used as published (versions and
  checksums in `docs/Third-Party.md` and `tools/README-a2ts.md`).

To report a vulnerability, please use GitHub's private vulnerability reporting for this repository
([Security tab, "Report a vulnerability"](https://github.com/arguingbananas/beyond-the-purple-door/security/advisories/new))
rather than opening a public issue. This is a one-person hobby project, so replies are best
effort. Fixes are made on `main` (there are no release branches), and the advisory is
published once a fix is in.

## Supply-chain decisions

- **Python dev tools are pinned exactly (`==`) but not hash-pinned** (decided 2026-11-20). They only
  check the code (lint, audit); nothing they produce is distributed, and every release users get
  (patchers, IPS files, scripts) is source written here. npm dev tools are already checksummed by
  `package-lock.json`. **Revisit before shipping any built artifact** (a packaged binary, a wheel, a
  release asset produced by a build step): then hash-pin build dependencies
  (`pip-compile --generate-hashes`, `pip install --require-hashes`) and add build provenance.
