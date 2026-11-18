#!/usr/bin/env bash
# Start Apple2TS headless in the background (no window) and restore the saved emulator state of the
# BCW cabinet room ($3C), leaving it PAUSED so the guard cannot catch anyone.
#   resume: node tools/a2ts_ctl.mjs setRunMode '{"runMode":-1}'     pause: ... '{"runMode":-2}'
# usage: tools/bcw_up.sh [state.a2ts]        stop with: tools/bcw_down.sh
# The state embeds the disk it was made with (local-patch v3); a patched disk needs a new state (menu steps in README-a2ts.md).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist="${A2TS_DIST:-$here/a2ts-web/dist}"
state="${1:-$here/a2ts-web/states/bcw-cabinet-room-local-v3.a2ts}"
ctl() { node "$here/tools/a2ts_ctl.mjs" "$@"; }
"$here/tools/bcw_down.sh" >/dev/null 2>&1 || true
nohup node "$here/tools/a2ts_bridge.mjs" --dist "$dist" --chromium >"${TMPDIR:-/tmp}/a2ts-bridge.log" 2>&1 &
for _ in $(seq 60); do ctl getStatus >/dev/null 2>&1 && break; sleep 1; done
sleep 5                                                  # the emulator worker starts a moment after the page connects
room=""
for _ in 1 2 3 4 5; do                                   # import, then verify rather than assume
  ctl importSaveState "{\"file\":\"$state\"}" >/dev/null 2>&1 || true
  ctl setRunMode '{"runMode":-1}' >/dev/null; sleep 2    # the screen only redraws while running
  ctl setRunMode '{"runMode":-2}' >/dev/null
  room=$(ctl getMemoryView '{"address":16464,"length":1,"space":"main"}' | tr -d ' \n' | grep -o '"bytes":\[[0-9]*\]' || true)
  [ "$room" = '"bytes":[60]' ] && break
  sleep 3
done
echo "paused, room byte at \$4050: $room   (60 = \$3C cabinet room)"
[ "$room" = '"bytes":[60]' ]
