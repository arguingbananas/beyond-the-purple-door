#!/usr/bin/env bash
# Stop the headless emulator started by bcw_up.sh (kills by PID; never use pkill -f from Claude Code).
for port in 8765; do
  pid=$(ss -ltnp 2>/dev/null | grep ":$port " | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
  [ -n "$pid" ] && kill "$pid"
done
for pid in $(ps -eo pid,args | awk '$2!~/bash/ && /a2ts-chromium/ && $2!="awk" {print $1}'); do kill "$pid"; done
sleep 1
