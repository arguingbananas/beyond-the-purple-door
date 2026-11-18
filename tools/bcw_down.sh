#!/usr/bin/env bash
# Stop the headless emulator started by bcw_up.sh (kills by PID; never use pkill -f from Claude Code).
pidfile="${TMPDIR:-/tmp}/a2ts-bridge.pid"
[ -f "$pidfile" ] || exit 0
pid=$(cat "$pidfile")
# only signal the process if it is still our bridge (guards against a recycled PID)
if tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q 'a2ts_bridge.mjs'; then
  kill "$pid"                                    # the bridge stops chromium and deletes its profile
  for _ in $(seq 50); do kill -0 "$pid" 2>/dev/null || break; sleep 0.1; done
fi
rm -f "$pidfile"
