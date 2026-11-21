# Beyond Castle Wolfenstein: Purple Door Local Patch

This patch modifies an **unprotected, 35-track DOS 3.3 `.dsk` image** of
*Beyond Castle Wolfenstein* (the 4am crack). It makes the purple barrier in
room `$3C`, the cabinet room, passable. The barrier is still drawn, but the
player can walk through it. No other collision check is changed: outer walls,
inner walls and the green closets still block movement.

Unlike the earlier *Terminal Barrier* patch, which changes shared player
collision code and affects every object, this patch changes data for one door
in one room.

## Known side effect

The collision entries the patch removes are shared by everyone. **Guards pass
through the opened door too.** A guard who sees you can walk through it and
catch you, so go straight to the door. The game does not need to be paused.
When you leave the room and come back, the room reloads and the door is
treated the same way, because the patch runs on every room load.

## Files

- `apply_bcw_purple_door_patch.py` — recommended patcher. It finds `@FHR` and
  `^THINGS` through the DOS catalog and T/S lists, checks the original bytes,
  and writes a **new** image. It imports helpers from
  `apply_bcw_terminal_patch.py`, so keep both files in the same directory.
- `bcw-purple-door-local.ips` — IPS patch for the standard raw DOS-order 4am
  image. It changes 28 bytes in three places. Use the Python patcher for other
  copies, whose files may sit in different sectors.

## Applying the patch

1. Back up your original image. The patcher never changes its input.
2. Put both `.py` files next to the image and run:

```sh
python3 ./apply_bcw_purple_door_patch.py "Beyond Castle Wolfenstein.dsk" "Beyond Castle Wolfenstein - Purple Door.dsk"
```

3. The patcher reports success only after verifying the expected bytes. If the
   image differs from what it expects, it stops without writing anything.

To use the IPS patch instead, apply `bcw-purple-door-local.ips` to a copy of
the 4am image with any IPS tool.

## How the game makes the door solid

1. The game keeps the current room in memory at `$4000–$40FF`. The map is at
   `$4000–$4047`, the exit flags at `$4048–$404D`, and the current room number
   at `$4050`. Objects are 16-byte records starting at `$4080`. The purple
   door is the record at `$40A0`.
2. Object collision uses two tables, `$4200,X` and `$4208,X`, with one byte per
   map cell. When the game tests a move, the code at `$1500` in `@FHR` reads
   `$4200,X`. A non-zero entry that holds an object's record number makes the
   cell solid.
3. When a room loads, a loop at `$0C4B` clears `$4200–$4247`. Then `^THINGS`
   (loaded at `$4800`) fills in the entries for each object. The routine at
   `$5D2A` does this:

   ```
   $5D2A  LDX $5E6B
   $5D2D  DEX
   $5D2E  LDA $6B        ; low byte of the object record, $A0 for the door
   $5D30  STA $4200,X
   $5D33  STA $4208,X
   ```

   For the purple door X is `$3D` after the `DEX`, and `$6B` is `$A0`.

Earlier attempts failed because they edited the map data at `$4047` and the
disk copies of the room map. The room loader at `$1AC2–$1B35` rebuilds the wall
bits from the exit flags on every load, so those edits were overwritten. The
map cell was never the purple door. The object tables were.

I confirmed this live: writing `00` to `$423D` and `$4245` in the running game
let the player walk through the barrier. A write watchpoint on `$423D` then
found the writer at `$5D33`.

## What the patch changes

### 1. A 24-byte stub at `@FHR $1EB3`

`@FHR` loads at `$810–$1EB2`. The area just after it is unused, and nothing in
the game references `$1EB3–$1EFF` other than the calls to `^DEMOHOREAD` at
`$1F00`. The patch appends this stub and raises the file's length field in its
binary header from 5795 to 5819 bytes.

```
$1EB3  CA        DEX
$1EB4  AD 50 40  LDA $4050     ; current room
$1EB7  C9 3C     CMP #$3C
$1EB9  D0 0D     BNE norm
$1EBB  E0 3D     CPX #$3D      ; purple door cell
$1EBD  D0 09     BNE norm
$1EBF  A5 6B     LDA $6B
$1EC1  C9 A0     CMP #$A0      ; door record $40A0
$1EC3  D0 03     BNE norm
$1EC5  A9 00     LDA #$00      ; no collision
$1EC7  60        RTS
$1EC8  A5 6B     norm: LDA $6B
$1ECA  60        RTS
```

In every case except room `$3C`, cell `$3D`, record `$A0`, the stub returns
exactly what the original `DEX` / `LDA $6B` produced.

### 2. The call site in `^THINGS` at `$5D2D`

The three bytes `CA A5 6B` (`DEX` / `LDA $6B`) become `20 B3 1E`
(`JSR $1EB3`). The rest of the routine is unchanged, so the table entries for
the purple door become `$00` and every other object is written as before.

### Byte-level summary (raw 4am image)

| Image offset | Length | Change |
|--------------|--------|--------|
| `0x17C02`    | 1      | `@FHR` length low byte, `0xA3` → `0xBB` |
| `0x186A7`    | 24     | stub written over `FF` padding |
| `0x1AF31`    | 3      | `CA A5 6B` → `20 B3 1E` |

## Testing

The patch was developed on a saved game in room `$3C` and tested live in
Apple2TS. After patching, the player walked through the purple barrier. Outer
walls, inner walls and closets still blocked. A guard also walked through the
barrier, which is the side effect described above. The pristine 4am image was
never modified, and the patcher's output on it was checked against the IPS
patch byte for byte.

## Limitations

- Passage is opened for guards as well as the player (see above).
- Only room `$3C` is affected.
- The stub is placed in `@FHR`'s trailing padding. If a different copy of the
  game lays out `@FHR` differently, the patcher refuses to continue.
