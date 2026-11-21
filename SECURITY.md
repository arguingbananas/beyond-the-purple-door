# Security policy

This repo contains disk-image patchers and local development tooling; it runs no public service.
The emulator bridge (`tools/a2ts_bridge.mjs`) listens on `127.0.0.1` only and rejects foreign
`Host` and `Origin` headers. The headless Chromium it starts is blocked from resolving any other
host, so it makes no outbound connections.

To report a vulnerability, please use GitHub's private vulnerability reporting for this repository
(Security tab, "Report a vulnerability") rather than opening a public issue.

## Supply-chain decisions

- **Python dev tools are pinned exactly (`==`) but not hash-pinned** (decided 2026-11-20). They only
  check the code (lint, audit); nothing they produce is distributed, and every release users get
  (patchers, IPS files, scripts) is source written here. npm dev tools are already checksummed by
  `package-lock.json`. **Revisit before shipping any built artifact** (a packaged binary, a wheel, a
  release asset produced by a build step): then hash-pin build dependencies
  (`pip-compile --generate-hashes`, `pip install --require-hashes`) and add build provenance.
