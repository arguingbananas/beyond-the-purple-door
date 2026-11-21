# Project notes: the purple door in Beyond Castle Wolfenstein

Goal: let the player walk through the purple door (a purple barrier) in the terminal/cabinet room of
*Beyond Castle Wolfenstein* (Muse, 1984, Apple II, DOS 3.3). The room is `$3C` in the game's own
numbering. `reference/objective-circled.png` shows it: the player circled green, the purple door boxed
red at the lower right, a guard on the far side.

All patches target the 4am crack of the game (a raw DOS-order, 143,360-byte, 35-track `.dsk`,
SHA-256 starting `5898ae8f`). The game image is not in this repo; supply your own.

## Status

| Approach | Scope | Result |
|---|---|---|
| **Local patch** (preferred) | Only room `$3C`, only the purple-door record | Player walks through. Walls and closets still block. **Guards walk through it too.** |
| Global terminal-barrier patch | Shared player collision code | Player walks through the door and probably other map walls. |

Not done: hiding the door graphic (`docs/Hide-Purple-Door-Notes.md`, untested guesses) and making the
door passable for the player only.

## How the door is solid

Details are in `docs/Purple-Door-Local-Patch.md`. In short:

- The current room lives at `$4000-$40FF`: map `$4000-$4047`, exit flags `$4048-$404D`, current room
  number `$4050`, objects as 16-byte records from `$4080`. **The purple door is the record at `$40A0`**
  (type byte `$60`; changing it to `$20` turns it into a green closet, so the type byte selects the
  sprite).
- Object collision uses two tables, `$4200,X` and `$4208,X`, one byte per map cell. The movement test
  reads `$4200,X`; a non-zero entry makes the cell solid.
- On every room load a loop clears `$4200-$4247`, then `^THINGS` (loaded at `$4800`) refills it
  (`$5D2A-$5D33`). The local patch changes the fill so the purple door's entries stay zero.
- **Dead ends:** editing the map bytes or the disk copies of the room map does nothing, because the
  room loader rebuilds the wall bits from the exit flags on every load. The map cell was never the
  barrier; the object tables are.
- Confirmed live: writing `$00` to `$423D` and `$4245` in the running game makes the barrier walkable,
  and a write watchpoint on `$423D` leads to the writer at `$5D33`.

## The patches

`patches/` holds Python patchers (standard library only; they locate files through the DOS catalog and
refuse to patch unless the original bytes match) and IPS files for the standard image. The two patchers
must stay in one directory: the door patcher imports the terminal one.

| File | Disk bytes changed | Contents |
|---|---|---|
| `bcw-purple-door-local.ips` | 28 | local patch only |
| `bcw-purple-door-with-savegame.ips` | 409 | local patch plus a saved game in room `$3C` |
| `bcw-terminal-barrier.ips` | 7 | global patch only |

IPS writes at absolute offsets, so apply it only to the standard image above.

## Verification

`tools/verify.sh` rebuilds everything from the 4am crack and checks hashes:

- patcher output equals the IPS output for both patches (`3d843c2c...` local, `758ba06d...` terminal);
- the saved-game IPS applied to the crack gives `ac664ef6...`;
- when CiderPress II is installed, `tools/cp2_check.py` finds each rebuilt image's DOS filesystem
  the same as the original's (same notes, usage counts and files; `cp2 test` alone is not enough);
- play-tested in Apple2TS: the player walks through the barrier, outer walls, inner walls and closets
  block, and a guard also walks through. A disk booted from the IPS-built copy was never booted itself;
  it is byte-identical to the image that was played.

To start the saved game at the demo screen: Esc, Return, K (keyboard), D (resume), Return. Play a copy;
the game writes to its disk. If a guard catches the player the game ends and the in-memory save is lost.

Background and headless emulator control: `tools/README-a2ts.md`.

## What is not known

- Whether anything else reads the `$40A0` record (guard logic, "door reappears" behaviour).
- Which individual fields of the saved game differ in the experimental images; they were never decoded.
- Whether the IPS-built image boots (see above).

## Ideas for next steps

1. Hide the door graphic: poke the type byte at `$40A0` to a few values with the game paused, then find
   the drawing code. The pixels may also be in the room background.
2. Player-only passage: guards use the same table, so this needs a separate player-collision lookup.
3. Boot-test an image built purely from the IPS.
4. Patches for `.woz`/`.nib` copies (currently DOS-order `.dsk` only).
