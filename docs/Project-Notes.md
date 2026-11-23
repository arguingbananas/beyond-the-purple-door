# Project notes: the purple door in Beyond Castle Wolfenstein

Goal: let the player walk through the purple door (a purple barrier) in the cabinet room of
*Beyond Castle Wolfenstein* (Muse, 1984, Apple II, DOS 3.3). The room is `$3C` in the game's own
numbering. `reference/objective-circled.png` shows it: the player circled green, the purple door boxed
red at the lower right, a guard on the far side.

All patches target the 4am crack of the game (a raw DOS-order, 143,360-byte, 35-track `.dsk`,
SHA-256 starting `5898ae8f`). The game image is not in this repo; supply your own.

## Status

| Approach | Scope | Result |
|---|---|---|
| **Local patch** (preferred) | Only room `$3C`, only the purple-door record | Player walks through. Walls and closets still block. **Guards walk through it too.** |
| Global terminal-barrier patch (removed 2026-11-22) | Shared player collision code | Player walked through the door and probably other map walls. Obsolete once the local patch worked; still in git history. |

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

## Who is in room `$3C`

Read from the room data with the game paused in room `$3C`, and from the game's text on the disk
(2026-11-22):

- **The figure behind the purple door is an ordinary guard.** It is not in the room's object list;
  it is an actor run by the same code as every other guard. The "HEIL !" shown on entering is the
  first line of the guards' speech table ("HEIL ! / YOUR PASS ! / COME HERE ! / STOP ! / NO ! /
  ALERT !"), and once the door is opened the guard walks through it like any other.
- **The seated cabinet is scenery.** The object list holds only the conference table (type `$50`),
  the purple door (`$60`), two green closets (`$20`) and one record not yet identified (`$10`). The
  table's collision cells (`$90` at `$4228-$422D` and `$4230-$4235`, two rows of six) cover the table
  and the seated figures: drawn and solid, otherwise inert.
- **Hitler is never drawn.** He appears only in item names ("HITLER'S DIARY") and in the ending
  telegrams: success reads "HITLER AND MOST OF CABINET DEAD", the partial failure "MAJOR EXPLOSION IN
  THE FUEHRERBUNKER ... FUEHRER ESCAPED UNHARMED ... TRY AGAIN". The working assumption is that the
  bomb going off in the cabinet room is a success and anywhere else is the partial failure; the code
  that picks the telegram has not been traced yet.

## The patches

`patches/` holds a Python patcher (standard library only; it locates files through the DOS catalog and
refuses to patch unless the original bytes match) and IPS files for the standard image. The patcher
imports `dos33.py` (catalog and sector helpers), so keep the two files in one directory.

| File | Disk bytes changed | Contents |
|---|---|---|
| `bcw-purple-door-local.ips` | 28 | local patch only |
| `bcw-purple-door-with-savegame.ips` | 409 | local patch plus a saved game in room `$3C` |

IPS writes at absolute offsets, so apply them only to the standard image above.

## Verification

`tools/verify.sh` rebuilds everything from the 4am crack and checks hashes:

- the patcher output equals the local IPS output (`3d843c2c...`);
- the saved-game IPS applied to the crack gives `ac664ef6...`;
- when CiderPress II is installed, `tools/cp2_check.py` finds each rebuilt image's DOS filesystem
  the same as the original's (same notes, usage counts and files; `cp2 test` alone is not enough);
- play-tested in Apple2TS: the player walks through the barrier, outer walls, inner walls and closets
  block, and a guard also walks through;
- boot-tested (2026-11-20, headless Apple2TS): the images built from the crack with the IPS
  files reach the title screen, and the saved-game image resumes into room `$3C`.

To start the saved game: at the title screen ("PRESS RETURN TO BEGIN") press Return, K (keyboard),
D (resume), Return; if the attract demo is running, press Esc first. Play a copy;
the game writes to its disk. If a guard catches the player the game ends and the in-memory save is lost.

Background and headless emulator control: `tools/README-a2ts.md`.

## What is not known

- Whether anything else reads the `$40A0` record (guard logic, "door reappears" behaviour).
- Which individual fields of the saved game differ in the experimental images; they were never decoded.
- What decides between the two ending telegrams (where the bomb goes off, when, or both), and what
  the `$10` object record in room `$3C` is.

## Ideas for next steps

1. Hide the door graphic: poke the type byte at `$40A0` to a few values with the game paused, then find
   the drawing code. The pixels may also be in the room background.
2. Player-only passage: guards use the same table, so this needs a separate player-collision lookup.
3. Patches for `.woz`/`.nib` copies (currently DOS-order `.dsk` only).
