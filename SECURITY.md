# Security policy

This repo contains disk-image patchers and local development tooling; it runs no public service.
The emulator bridge (`tools/a2ts_bridge.mjs`) listens on `127.0.0.1` only and rejects foreign
`Host` and `Origin` headers. The headless Chromium it starts is blocked from resolving any other
host, so it makes no outbound connections.

To report a vulnerability, please use GitHub's private vulnerability reporting for this repository
(Security tab, "Report a vulnerability") rather than opening a public issue.
